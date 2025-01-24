import streamlit as st
import yt_dlp
import os
import subprocess
from pathlib import Path

def check_ffmpeg():
    try:
        subprocess.run(["ffmpeg", "-version"], capture_output=True, check=True)
        return True
    except:
        return False

def get_video_info(url):
    ydl_opts = {'quiet': True}
    with yt_dlp.YoutubeDL(ydl_opts) as ydl:
        return ydl.extract_info(url, download=False)

def get_quality_options(info):
    formats = []
    seen = set()
    
    for f in info['formats']:
        if f.get('vcodec') != 'none':
            res = f.get('height')
            if res:
                label = f"{res}p | {f.get('fps', '')}fps | {f.get('ext', '').upper()}"
                if res not in seen:
                    formats.append((label, f['format_id']))
                    seen.add(res)
    
    formats.sort(key=lambda x: int(x[0].split('p')[0]), reverse=True)
    return formats

def download_video(url, format_id):
    try:
        ydl_opts = {
            'format': f'{format_id}+bestaudio/best',
            'outtmpl': os.path.join('downloads', '%(title)s.%(ext)s'),
            'merge_output_format': 'mp4',
            'quiet': True,
        }

        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
            info = ydl.extract_info(url)
            filename = ydl.prepare_filename(info)
            return filename, info['title']
    except Exception as e:
        st.error(f"Download error: {str(e)}")
        return None, None

# Streamlit UI
st.set_page_config(
    page_title="YouTube Downloader",
    page_icon="🎬",
    layout="centered"
)

st.title("YouTube Video Downloader 🎥")
st.markdown("### Download videos in maximum quality")

# Check FFmpeg
if not check_ffmpeg():
    st.error("FFmpeg not found! Please wait while we install it...")
    st.stop()

# Create downloads directory
Path("downloads").mkdir(exist_ok=True)

# URL input
url = st.text_input("Enter YouTube URL:", placeholder="https://youtube.com/watch?v=...")

if url:
    try:
        with st.spinner("Fetching video info..."):
            info = get_video_info(url)
            
            if info:
                st.subheader("Video Details")
                col1, col2 = st.columns(2)
                col1.markdown(f"**Title:** {info['title']}")
                col2.markdown(f"**Duration:** {info['duration'] // 60} mins")
                
                quality_options = get_quality_options(info)
                selected = st.selectbox(
                    "Select Quality:",
                    options=[q[0] for q in quality_options],
                    index=0
                )
                format_id = quality_options[[q[0] for q in quality_options].index(selected)][1]

if st.button("Download Video"):
    if url and format_id:
        with st.spinner("Downloading..."):
            file_path, title = download_video(url, format_id)
            
            if file_path:
                st.success("Download complete!")
                with open(file_path, "rb") as f:
                    st.download_button(
                        "Save Video",
                        data=f,
                        file_name=os.path.basename(file_path),
                        mime="video/mp4"
                    )
                Path(file_path).unlink()
    else:
        st.warning("Please enter a valid URL")

st.markdown("---")
st.caption("Note: For educational purposes only. Respect copyright laws.")
