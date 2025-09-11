# Video Downloader API

This API allows you to download a video from a URL, store it on a server, and receive a temporary download link.

**Base URL**: `http://<your-ec2-ip-address>:5000`

---
### Endpoints

#### 1. Start a Download

Initiates the download and upload process for a video. This is an asynchronous operation.

* **URL**: `/download`
* **Method**: `POST`
* **Request Body**:
    ```json
    {
      "url": "[https://www.youtube.com/watch?v=your_video_id](https://www.youtube.com/watch?v=your_video_id)"
    }
    ```
* **Success Response (202 Accepted)**:
    The task has been accepted. Use the `task_id` to check the status.
    ```json
    {
      "message": "Download task has been accepted.",
      "task_id": "a1b2c3d4-e5f6-g7h8-i9j0-k1l2m3n4o5p6"
    }
    ```
* **Error Response (400 Bad Request)**:
    ```json
    {
      "error": "URL is required in the JSON body."
    }
    ```

#### 2. Get Download Status and Link

Checks the status of a download task. If successful, it provides a temporary download URL.

* **URL**: `/status/<task_id>`
* **Method**: `GET`
* **URL Parameters**:
    * `task_id` (string, required): The ID returned from the `/download` endpoint.
* **Success Response (200 OK)**:

    * *If the task is still pending or running:*
        ```json
        {
          "task_id": "a1b2c3d4-e5f6-g7h8-i9j0-k1l2m3n4o5p6",
          "status": "PENDING"
        }
        ```
    * *If the task completed successfully:*
        ```json
        {
          "task_id": "a1b2c3d4-e5f6-g7h8-i9j0-k1l2m3n4o5p6",
          "status": "SUCCESS",
          "download_url": "[https://your-s3-bucket.s3.amazonaws.com/video.mp4?AWSAccessKeyId=](https://your-s3-bucket.s3.amazonaws.com/video.mp4?AWSAccessKeyId=)..."
        }
        ```
    * *If the task failed:*
        ```json
        {
          "task_id": "a1b2c3d4-e5f6-g7h8-i9j0-k1l2m3n4o5p6",
          "status": "FAILURE",
          "result": "Error: Download failed because..."
        }
        ```
