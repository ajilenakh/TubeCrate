# To start the API

step-1: cd into the backend directory

```cd backend```

step-2: create a virtual envirement for the API
```python -m venv venv```
           OR
```python3 -m venv venv```

step-3: start the virtual enviorement

*linux/mac*
```source /venv/bin/activate```
*windows*
```venv\Scripts\activate```

step-4: install the requirements
```pip install -r \path\to\requirements.txt```

step-5: install yt-dlp
"https://github.com/yt-dlp/yt-dlp?tab=readme-ov-file#installation"

step-6 start the API
```uvicorn main:app --reload --host 0.0.0.0 --port 8000```

____________________________________________________________________________________________________________________


# Endpoints

1. Get Highest Resolution Video Formats

Endpoint: GET /filter_resolution/

Description:
Fetches the available video formats for a given URL and returns the highest resolution for each format.

Query Parameters:

    url (str): The URL of the video to retrieve information from.

Response: A list of dictionaries containing the format details with the highest file size for each resolution:

```[
  {
    "format_note": "1080p",
    "highest_filesize": 3492738,
    "format_id": "137"
  },
  {
    "format_note": "720p",
    "highest_filesize": 2053120,
    "format_id": "22"
  }
]
```
Example Request:

GET /filter_resolution/?url=https://www.youtube.com/watch?v=abcd1234

2. Process Video

Endpoint: POST /process_video/

Description:
Processes a video for download in a specified format.

Request Body:
```
{
  "url": "https://www.youtube.com/watch?v=abcd1234",
  "video_format_id": "137"
}
```
url (str): The URL of the video to download.
video_format_id (str): The format ID (from the previous endpoint) to specify which format to download.

Response: Returns a unique ID for the download and the processed file name:

{
  "unique_id": "a1b2c3d4-e5f6-7g8h9i0j",
  "file_name": "video_title.mp4"
}

Example Request:

```
POST /process_video/ 
Content-Type: application/json
{
  "url": "https://www.youtube.com/watch?v=abcd1234",
  "video_format_id": "137"
}
```
3. Download Processed Video

Endpoint: GET /videos/{unique_id}/{file_name}

Description:
Downloads the processed video based on the unique ID and file name provided.

Path Parameters:

unique_id (str): The unique ID generated when processing the video.
file_name (str): The name of the processed video file.

Response: The video file is returned as a downloadable attachment.

Example Request:

```GET /videos/a1b2c3d4-e5f6-7g8h9i0j/video_title.mp4```

Response: The processed video will be returned as a downloadable file.
