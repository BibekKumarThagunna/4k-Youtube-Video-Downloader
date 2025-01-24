import streamlit as st
import yt_dlp
import os
from pathlib import Path

def get_video_info(url):
    ydl_opts = {'quiet': True}
    try:
        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
            info = ydl.extract_info(url, download=False)
            return info
    except Exception as e:
        st.error(f"Error getting video info: {str(e)}")
        return None

def get_quality_options(info):
    if not info:
        return []
    
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

        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
            info = ydl.extract_info(url)
            filename = ydl.prepare_filename(info)
            return filename, info['title']
    except Exception as e:
        st.error(f"Download error: {str(e)}")
        return None, None

def progress_hook(d):
    if d['status'] == 'downloading' and 'downloaded_bytes' in d:
        progress = d.get('_percent_str', '0%').strip('%')
        try:
            progress_float = float(progress)
            progress_bar.progress(int(progress_float))
        except:
            pass

# Streamlit UI configuration
st.set_page_config(
    page_title="YouTube DL Quality Selector",
    page_icon="🎥",
    layout="centered"
)

st.title("YouTube Video Downloader 🎬")
st.markdown("### Download videos in your preferred quality")

# Initialize session state variables
if 'selected_format' not in st.session_state:
    st.session_state.selected_format = None

# URL input
url = st.text_input("Enter YouTube URL:", placeholder="https://youtube.com/watch?v=...")

# Create downloads directory if not exists
Path("downloads").mkdir(exist_ok=True)

# Initialize progress bar
progress_bar = st.progress(0)

# Main processing logic
if url:
    try:
        with st.spinner("Fetching video info..."):
            info = get_video_info(url)
            
            if info:
                # Display video details
                col1, col2 = st.columns(2)
                with col1:
                    st.markdown(f"**Title:** {info['title']}")
                    st.markdown(f"**Channel:** {info['uploader']}")
                with col2:
                    st.markdown(f"**Duration:** {info['duration']} seconds")
                    st.markdown(f"**Views:** {info['view_count']:,}")
                
                # Quality selection
                st.subheader("Select Video Quality")
                quality_options = get_quality_options(info)
                
                if quality_options:
                    selected_label = st.selectbox(
                        "Available Qualities:",
                        options=[q[0] for q in quality_options],
                        index=0
                    )
                    st.session_state.selected_format = quality_options[[q[0] for q in quality_options].index(selected_label)][1]
                else:
                    st.error("No video formats available for this content")

    except Exception as e:
        st.error(f"Error processing video: {str(e)}")

# Download button
if st.button("Download Video"):
    if url and st.session_state.selected_format:
        try:
            with st.spinner("Downloading..."):
                file_path, title = download_video(url, st.session_state.selected_format)
                
                if file_path:
                    st.success("Download complete! 🎉")
                    st.balloons()
                    
                    with open(file_path, "rb") as f:
                        st.download_button(
                            label="Save Video",
                            data=f,
                            file_name=os.path.basename(file_path),
                            mime="video/mp4"
                        )
                    
                    Path(file_path).unlink()
        except Exception as e:
            st.error(f"Download failed: {str(e)}")
    else:
        st.warning("Please enter a valid YouTube URL and select quality first")

# Sidebar information
with st.sidebar:
    st.markdown("## Features")
    st.markdown("""
    - Quality selection (up to 8K)
    - Automatic audio merging
    - Multiple format support
    - Progress indicators
    - Video metadata display
    """)
    
    st.markdown("## Requirements")
    st.markdown("""
    - FFmpeg installed
    - Python 3.7+
    - yt-dlp package
    """)

# Footer
st.markdown("---")
st.caption("Note: This tool is for personal use only. Respect copyright laws.")
st.caption("Note: This Project is Created By Bibek Kumar Thagunna")
