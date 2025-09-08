import os
import yt_dlp
import boto3
from celery import Celery

# Use your ElastiCache Primary Endpoint here
REDIS_URL = "redis://clustercfg.video-downloader-redis.avlitx.aps1.cache.amazonaws.com:6379"
S3_BUCKET_NAME = "video-downloader-bucket"

celery_app = Celery('tasks', broker=REDIS_URL, backend=REDIS_URL)

celery_app.conf.update(
    worker_direct=True,
    broker_transport_options={
        # 'queue_name_prefix': '{video-downloader}',
        'fanout_prefix': True,
        'fanout_patterns': True,
    },
    result_backend_transport_options={
        # 'queue_name_prefix': '{video-downloader}',
        'fanout_prefix': True,
        'fanout_patterns': True,
    }
)


@celery_app.task(name='tasks.download_video')
def download_video_task(video_url):
    # We will download the file to a temporary location on the server
    temp_dir = "/tmp" 
    ydl_opts = {
        'outtmpl': os.path.join(temp_dir, '%(id)s.%(ext)s'),
    }

    try:
        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
            info = ydl.extract_info(video_url, download=True)
            # Get the path of the downloaded file
            downloaded_file_path = ydl.prepare_filename(info)
            file_name = os.path.basename(downloaded_file_path)

        # Upload the file from the temporary location to S3
        s3_client = boto3.client('s3')
        s3_client.upload_file(downloaded_file_path, S3_BUCKET_NAME, file_name)
        
        # Clean up the temporary file
        os.remove(downloaded_file_path)
        
        # Return the S3 file key so the API can generate a download link
        return {'status': 'Success', 's3_key': file_name}
    except Exception as e:
        raise e