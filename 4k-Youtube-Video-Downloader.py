import streamlit as st
import yt_dlp 
import os
from pathlib import Path

def get_video_info(url):
    ydl_opts = {'quiet': True}
    with yt_dlp.YoutubeDL(ydl_opts) as ydl:  # Use yt_dlp directly
        info = ydl.extract_info(url, download=False)
        return info

def get_quality_options(info):
    """Extract available video resolutions and format IDs"""
    formats = []
    seen = set()
    
    for f in info['formats']:
        if f.get('vcodec') != 'none':
            res = f.get('height', 'Unknown')
            fps = f.get('fps', 0)
            fmt_note = f.get('format_note', 'N/A')
            ext = f.get('ext', 'mp4')
            
            label_parts = []
            if res: label_parts.append(f"{res}p")
            if fps: label_parts.append(f"{int(fps)}fps")
            if fmt_note: label_parts.append(fmt_note)
            label_parts.append(ext.upper())
            
            label = " ".join(label_parts)
            if res and res not in seen:
                formats.append((label, f['format_id']))
                seen.add(res)
    
    formats.sort(key=lambda x: int(x[0].split('p')[0]) if x[0][0].isdigit() else 0, reverse=True)
    return formats

def download_video(url, format_id):
    try:
        ydl_opts = {
            'format': f'{format_id}+bestaudio/best',
            'outtmpl': os.path.join('downloads', '%(title)s.%(ext)s'),
            'merge_output_format': 'mp4',
            'quiet': True,
            'progress_hooks': [progress_hook],
        }

        with yt_dlp.YoutubeDL(ydl_opts) as ydl:  # Use yt_dlp directly
            info = ydl.extract_info(url)
            filename = ydl.prepare_filename(info)
            return filename, info['title']
    except Exception as e:
        st.error(f"Error: {str(e)}")
        return None, None

# ... (rest of the code remains the same) ...
