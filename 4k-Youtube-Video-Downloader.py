import streamlit as st
import yt_dlp as youtube_dl
import os
from pathlib import Path

def get_video_info(url):
    ydl_opts = {'quiet': True}
    with youtube_dl.YoutubeDL(ydl_opts) as ydl:
        info = ydl.extract_info(url, download=False)
        return info

def download_video(url):
    try:
        # Set up download options
        ydl_opts = {
            'format': 'bestvideo+bestaudio/best',
            'outtmpl': os.path.join('downloads', '%(title)s.%(ext)s'),
            'merge_output_format': 'mp4',
            'quiet': True,
            'progress_hooks': [progress_hook],
        }

        with youtube_dl.YoutubeDL(ydl_opts) as ydl:
            info = ydl.extract_info(url)
            filename = ydl.prepare_filename(info)
            return filename, info['title']
    except Exception as e:
        st.error(f"Error: {str(e)}")
        return None, None

def progress_hook(d):
    if d['status'] == 'downloading':
        progress = d.get('_percent_str', '0%').strip('%')
        try:
            progress_float = float(progress)
            progress_bar.progress(int(progress_float))
        except:
            pass

# Streamlit UI configuration
st.set_page_config(
    page_title="YouTube DL Max Quality",
    page_icon="🎥",
    layout="centered"
)

st.title("YouTube Max Quality Downloader 🎬")
st.markdown("### Download videos in their maximum available quality (including 4K)")

# URL input
url = st.text_input("Enter YouTube URL:", placeholder="https://youtube.com/watch?v=...")

# Initialize progress bar
progress_bar = st.progress(0)

if st.button("Download Video"):
    if url:
        with st.spinner("Fetching video info..."):
            try:
                # Get video info first
                info = get_video_info(url)
                
                # Display video details
                col1, col2 = st.columns(2)
                with col1:
                    st.markdown(f"**Title:** {info['title']}")
                    st.markdown(f"**Channel:** {info['uploader']}")
                with col2:
                    st.markdown(f"**Duration:** {info['duration']} seconds")
                    st.markdown(f"**Views:** {info['view_count']:,}")
                
                # Start download
                with st.spinner("Downloading..."):
                    file_path, title = download_video(url)
                    
                    if file_path:
                        st.success("Download complete!")
                        st.balloons()
                        
                        # Show download button
                        with open(file_path, "rb") as f:
                            st.download_button(
                                label="Save Video",
                                data=f,
                                file_name=os.path.basename(file_path),
                                mime="video/mp4"
                            )
                        
                        # Clean up downloaded file
                        Path(file_path).unlink()
            except Exception as e:
                st.error(f"Error: {str(e)}")
    else:
        st.warning("Please enter a valid YouTube URL")

# Sidebar information
with st.sidebar:
    st.markdown("## Features")
    st.markdown("""
    - Supports 4K/8K downloads (when available)
    - Best audio/video quality
    - Multiple format support
    - Progress indicators
    - Video metadata display
    """)
    
    st.markdown("## Supported Sites")
    st.markdown("""
    Works with:
    - YouTube
    - Vimeo
    - Facebook
    - Twitter
    - Many more
    """)
    
    st.markdown("## Requirements")
    st.markdown("""
    - FFmpeg (for format merging)
    - yt-dlp (backend)
    - Python 3.7+
    """)

# Footer
st.markdown("---")
st.caption("Note: This tool is for personal use only. Respect copyright laws.")

# Create downloads directory if not exists
Path("downloads").mkdir(exist_ok=True)