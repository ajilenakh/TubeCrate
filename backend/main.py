from fastapi import FastAPI, HTTPException, BackgroundTasks
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import FileResponse
from pydantic import BaseModel
from pathlib import Path
import unicodedata
import subprocess
import shutil
import emoji
import json
import uuid
import time
import re
import os

#allowed_origins = ["http://0.0.0.0:5500"]

app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["GET", "POST"],
    allow_headers=["*"],
)

ENCODING_DIR = "temp"
os.makedirs(ENCODING_DIR, exist_ok=True)

class URLRequest(BaseModel):
    url: str

class VideoRequest(BaseModel):
    url: str
    video_format_id: str

def clean_title(title: str) -> str:
    # Normalize Unicode characters (e.g., converting accented characters to basic ASCII)
    title = unicodedata.normalize('NFKD', title)
    title = ''.join([c for c in title if not unicodedata.combining(c)])  # Remove combining characters

    title = emoji.replace_emoji(title, replace='')  # Remove emojis entirely, or replace with a placeholder

    title = re.sub(r'[<>:"/\\|?*]', '', title)

    title = re.sub(r'\s+', '_', title)  # Replace spaces with underscores
    title = re.sub(r'[^a-zA-Z0-9-_]', '', title)  # Remove anything that isn't a letter, number, or basic separator

    # Strip leading/trailing whitespace
    title = title.strip()

    if not title:
        title = "Untitled"

    return title


def delete_old_directory(directory_path: Path):
    """
    DELETE THE DIRECTORIES AFTER 24 HOURS
    """
    time.sleep(86400)
    if directory_path.exists() and directory_path.is_dir():
        shutil.rmtree(directory_path)
        print(f"Directory {directory_path} deleted after 24 hours.")

@app.get("/filter_resolution/")
async def filter_resolution(url: str):
    highest_sizes = {}

    # Running yt-dlp to get video information
    result = subprocess.run(['yt-dlp', '--dump-json', url], stdout=subprocess.PIPE, text=True)
    
    # Checking if the command was successful
    if result.returncode != 0:
        raise HTTPException(status_code=400, detail="Failed to fetch video information")

    video_info = json.loads(result.stdout)

    if 'formats' not in video_info:
        raise HTTPException(status_code=400, detail="No formats available in video information")

    formats = video_info['formats']

    for format in formats:
        format_note = format.get('format_note')
        filesize = format.get('filesize')
        format_id = format.get('format_id')

        if format_note is not None and filesize is not None:
            # If the format note is already in the dictionary, compare sizes
            if format_note in highest_sizes:
                # Save the highest file size, but also include the format_id
                highest_sizes[format_note]['highest_filesize'] = max(
                    highest_sizes[format_note]['highest_filesize'], filesize)
            else:
                highest_sizes[format_note] = {
                    'highest_filesize': filesize,
                    'format_id': format_id,
                }

    # Prepare the result to return
    format_res = [{
        "format_note": note,
        "highest_filesize": size_data['highest_filesize'],
        "format_id": size_data['format_id'],
    } for note, size_data in highest_sizes.items()]

    return format_res

@app.post("/process_video/")
async def process_video(request: VideoRequest, background_tasks: BackgroundTasks):
    url = request.url.strip()
    video_format_id = request.video_format_id.strip()

    # Generate a unique directory ID for this download
    unique_id = str(uuid.uuid4())

    # Define yt-dlp command with the correct output path
    ydl_cmd = [
        'yt-dlp', 
        '-f', f'{video_format_id}+bestaudio',
        '--merge-output-format', 'mp4',
        '--output', f'{ENCODING_DIR}/{unique_id}/%(title)s.%(ext)s',
        url
    ]

    try:
        subprocess.run(ydl_cmd, check=True)

        video_path = Path(f"{ENCODING_DIR}/{unique_id}")
        base_path = video_path
        to_delete = video_path
        files = list(video_path.iterdir())

        if len(files) == 1:
            video_path = files[0]
        else:
            raise HTTPException(status_code=404, detail="Download failed or multiple files found.")

        cleaned_title= clean_title(video_path.stem)

        new_video_path = video_path.with_name(f"{cleaned_title}{video_path.suffix}")
        video_path.rename(new_video_path)

        # Use background_tasks to schedule the directory deletion after 24 hours
        background_tasks.add_task(delete_old_directory, video_path.parent)

        file_name = str(new_video_path.name)

        print(unique_id,file_name)
        
        return {
            'unique_id': unique_id,
            'file_name': file_name,
        }
        

    except subprocess.CalledProcessError as e:
        raise HTTPException(status_code=400, detail=f"Error during video processing: {e}")

@app.get("/videos/{unique_id}/{file_name}")
async def download_video(unique_id: str, file_name: str):
    video_file_path = Path(f"{ENCODING_DIR}/{unique_id}/{file_name}")
    if video_file_path.exists() and video_file_path.is_file():
        return FileResponse(
            video_file_path,
            headers={"Content-Disposition": f"attachment; filename={file_name}"}
        )
    raise HTTPException(status_code=404, detail="File not found")