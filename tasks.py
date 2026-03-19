import os
import yt_dlp
import boto3
from celery import Celery

REDIS_URL = "redis://localhost:6379/1"
S3_BUCKET_NAME = "video-downloader-bucket-aman-vd-1"

celery_app = Celery('tasks', broker=REDIS_URL, backend=REDIS_URL)

celery_app.conf.update(
    worker_direct=True,
)


@celery_app.task(name='tasks.download_video')
def download_video_task(video_url):
    # We will download the file to a temporary location on the server
    project_dir = os.path.dirname(os.path.abspath(__file__))
    temp_dir = os.path.join(project_dir, "downloads")
    ydl_opts = {
        'outtmpl': os.path.join(temp_dir, '%(id)s.%(ext)s'),
        'format': 'best',
        'noplaylist': True,
        'cookiefile': os.path.join(project_dir, 'cookies.txt'),
        'http_headers': {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/58.0.3029.110 Safari/537.3'
        }
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