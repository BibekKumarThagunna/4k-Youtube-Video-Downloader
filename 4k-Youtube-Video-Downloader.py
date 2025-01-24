import streamlit as st
import yt_dlp
import io

# Get video information
def get_video_info(url):
    ydl_opts = {
        'quiet': True,
        'cookiefile': 'cookies.txt',  # Path to cookies.txt (optional)
    }
    try:
        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
            return ydl.extract_info(url, download=False)
    except Exception as e:
        st.error(f"Error getting video info: {str(e)}")
        return None

# Get quality options from video info
def get_quality_options(info):
    if not info:
        return []

    formats = []
    seen = set()

    for f in info['formats']:
        if f.get('vcodec') != 'none':  # Include only video formats
            res = f.get('height')
            if res:
                label = f"{res}p | {f.get('fps', '')}fps | {f.get('ext', '').upper()}"
                if res not in seen:
                    formats.append((label, f['format_id']))
                    seen.add(res)

    formats.sort(key=lambda x: int(x[0].split('p')[0]), reverse=True)
    return formats

# Download video into memory
def download_video_to_memory(url, format_id):
    try:
        ydl_opts = {
            'format': f'{format_id}+bestaudio/best',
            'outtmpl': '-',
            'merge_output_format': 'mp4',
            'quiet': True,
            'cookiefile': 'cookies.txt',  # Path to cookies.txt (optional)
            'outtmpl': '-',  # Output directly to memory
        }

        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
            info = ydl.extract_info(url)
            buffer = io.BytesIO()
            with ydl.stream_download(buffer):
                pass

            buffer.seek(0)
            return buffer, info['title'] + ".mp4"
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
st.markdown("### Download videos in your desired quality")

# URL input
url = st.text_input("Enter YouTube URL:", placeholder="https://youtube.com/watch?v=...")

format_id = None  # Initialize variable
quality_options = []  # Store quality options

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
                if quality_options:
                    selected = st.selectbox(
                        "Select Quality:",
                        options=[q[0] for q in quality_options],
                        index=0
                    )
                    format_id = quality_options[[q[0] for q in quality_options].index(selected)][1]
                else:
                    st.error("No available formats found")
    except Exception as e:
        st.error(f"Error processing URL: {str(e)}")

if st.button("Download Video"):
    if url and format_id:
        try:
            with st.spinner("Preparing video for download..."):
                video_data, filename = download_video_to_memory(url, format_id)

                if video_data:
                    st.success("Video is ready for download!")
                    st.download_button(
                        label="Download Video",
                        data=video_data,
                        file_name=filename,
                        mime="video/mp4"
                    )
        except Exception as e:
            st.error(f"Download failed: {str(e)}")
    else:
        st.warning("Please enter a valid URL and select quality")

# Footer
st.markdown("---")
st.caption("**This Project is Created By Bibek Kumar Thagunna**. For educational purposes only. Respect copyright laws.")
