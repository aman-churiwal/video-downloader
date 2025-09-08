from flask import Flask, request, jsonify
from tasks import download_video_task
import boto3

app = Flask(__name__)
print("HERE")
S3_BUCKET_NAME = "video-downloader-bucket"

@app.route('/download', methods=['POST'])
def start_download():
    data = request.get_json()
    if not data or 'url' not in data:
        return jsonify({'error': 'URL is required in the JSON body.'}), 400
    task = download_video_task.delay(data['url'])
    return jsonify({'message': 'Download task has been accepted.', 'task_id': task.id}), 202

@app.route('/status/<task_id>', methods=['GET'])
def get_task_status(task_id):
    task_result = download_video_task.AsyncResult(task_id)
    response = {'task_id': task_id, 'status': task_result.state}

    if task_result.state == 'SUCCESS':
        s3_key = task_result.result.get('s3_key')
        # Generate a temporary, secure link to the file in S3
        s3_client = boto3.client('s3')
        download_url = s3_client.generate_presigned_url(
            'get_object',
            Params={'Bucket': S3_BUCKET_NAME, 'Key': s3_key},
            ExpiresIn=3600  # Link is valid for 1 hour
        )
        response['download_url'] = download_url
    elif task_result.state == 'FAILURE':
        response['result'] = str(task_result.info) # Include error info

    return jsonify(response)