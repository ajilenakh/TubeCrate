from fastapi import FastAPI, HTTPException
import subprocess
import os
import json
from pydantic import BaseModel

app = FastAPI()

ENCODING_DIR = "temp"
os.makedirs(ENCODING_DIR, exist_ok=True)

class URLRequest(BaseModel):
    url: str

@app.post("/filter_resolution/")
async def filter_resolution(request: URLRequest):
    url = request.url
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

    # Printing the result 
    print(json.dumps(format_res, indent=4))

    return format_res