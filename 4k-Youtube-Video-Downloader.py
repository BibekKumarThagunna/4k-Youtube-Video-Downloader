import streamlit as st
import yt_dlp
import os
import shutil
import subprocess
from pathlib import Path

# Enhanced FFmpeg detection
def check_ffmpeg():
    try:
        # Check both PATH and common install locations
        ffmpeg_path = shutil.which("ffmpeg") or \
                     os.path.exists("/usr/bin/ffmpeg") or \
                     os.path.exists("C:/ffmpeg/bin/ffmpeg.exe")
        
        # Verify FFmpeg functionality
        if ffmpeg_path:
            result = subprocess.run(["ffmpeg", "-version"], capture_output=True, text=True)
            return "ffmpeg version" in result.stdout
        return False
    except Exception as e:
        return False

def get_video_info(url):
    ydl_opts = {'quiet': True}
    try:
        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
            return ydl.extract_info(url, download=False)
    except Exception as e:
        st.error(f"Error getting video info: {str(e)}")
        return None

def get_quality_options(info):
    formats = []
    seen = set()
    if not info:
        return formats

    for f in info.get('formats', []):
        if f.get('vcodec') != 'none':
            res = f.get('height')
            if not res:
                continue
                
            fps = f.get('fps', 0)
            fmt_note = f.get('format_note', 'N/A')
            ext = f.get('ext', 'mp4')
            codec = f.get('vcodec', '').split('.')[0]

            label = f"{res}p | {fps}fps | {fmt_note} | {codec} | {ext.upper()}"
            if res not in seen:
                formats.append((label, f['format_id']))
                seen.add(res)

    formats.sort(key=lambda x: x[0].split('p')[0], reverse=True)
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

        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
            info = ydl.extract_info(url)
            filename = ydl.prepare_filename(info)
            return filename, info['title']
    except Exception as e:
        st.error(f"Download error: {str(e)}")
        return None, None

def progress_hook(d):
    if d['status'] == 'downloading':
        progress = d.get('_percent_str', '0%').strip('%')
        try:
            st.session_state.progress = min(100, int(float(progress)))
        except:
            pass

# Streamlit UI Configuration
st.set_page_config(
    page_title="YT Premium Downloader",
    page_icon="🎬",
    layout="centered",
    initial_sidebar_state="expanded"
)

# FFmpeg Check and Installation Guide
if not check_ffmpeg():
    st.error("""
    ⚠️ FFmpeg not detected! Follow these steps:
    1. Install FFmpeg for your OS (see sidebar)
    2. Add FFmpeg to PATH
    3. Restart this application
    """)
    st.stop()

# Session State Initialization
if 'progress' not in st.session_state:
    st.session_state.progress = 0
if 'selected_format' not in st.session_state:
    st.session_state.selected_format = None

# Main UI
st.title("YouTube Premium Downloader 🎥")
st.markdown("### Download videos in any quality up to 8K")

# Sidebar with Installation Guide
with st.sidebar:
    st.header("FFmpeg Installation Guide")
    os_type = st.selectbox("Select Your OS:", ["Windows", "MacOS", "Linux"])
    
    if os_type == "Windows":
        st.markdown("""
        1. Download from [official build](https://www.gyan.dev/ffmpeg/builds/)
        2. Extract zip to `C:\\ffmpeg`
        3. Add to PATH:
           - Win + S → "Environment Variables"
           - Edit Path → Add `C:\\ffmpeg\\bin`
        4. Restart computer
        """)
    elif os_type == "MacOS":
        st.markdown("""
        ```bash
        # Install Homebrew if needed
        /bin/bash -c "$(curl -fsSL https://raw.githubusercontent.com/Homebrew/install/HEAD/install.sh)"
        
        # Install FFmpeg
        brew install ffmpeg
        """)
    else:  # Linux
        st.markdown("""
        ```bash
        # Ubuntu/Debian
        sudo apt update && sudo apt install ffmpeg -y
        
        # Fedora
        sudo dnf install ffmpeg
        ``` 
        """)
    
    st.markdown("### Verify Installation")
    st.code("ffmpeg -version", language="bash")

# Download Logic
Path("downloads").mkdir(exist_ok=True)
url = st.text_input("Enter YouTube URL:", placeholder="https://youtube.com/watch?v=...")

if url:
    with st.spinner("Analyzing video..."):
        info = get_video_info(url)
        if info:
            col1, col2 = st.columns(2)
            with col1:
                st.subheader("Video Details")
                st.markdown(f"**Title:** {info['title']}")
                st.markdown(f"**Channel:** {info['uploader']}")
                st.markdown(f"**Duration:** {info['duration'] // 60} minutes")
                
            with col2:
                st.subheader("Statistics")
                st.markdown(f"**Views:** {info['view_count']:,}")
                st.markdown(f"**Category:** {info.get('categories', ['Unknown'])[0]}")
                st.markdown(f"**Upload Date:** {info.get('upload_date', 'Unknown')}")
            
            quality_options = get_quality_options(info)
            if quality_options:
                selected = st.selectbox(
                    "Select Video Quality:",
                    options=[q[0] for q in quality_options],
                    index=0
                )
                st.session_state.selected_format = quality_options[[q[0] for q in quality_options].index(selected)][1]
            else:
                st.error("No downloadable formats found")

# Download Controls
progress_bar = st.progress(st.session_state.progress)

if st.button("Start Download", type="primary"):
    if url and st.session_state.selected_format:
        try:
            with st.spinner("Downloading..."):
                file_path, title = download_video(url, st.session_state.selected_format)
                
                if file_path:
                    st.success("Download Complete!")
                    st.balloons()
                    
                    with open(file_path, "rb") as f:
                        st.download_button(
                            "Save Video",
                            data=f,
                            file_name=os.path.basename(file_path),
                            mime="video/mp4"
                        )
                    
                    Path(file_path).unlink(missing_ok=True)
                    st.session_state.progress = 0
        except Exception as e:
            st.error(f"Download failed: {str(e)}")
    else:
        st.warning("Please enter a valid URL and select quality")

st.markdown("---")
st.caption("© 2024 YouTube Downloader | For educational purposes only")
