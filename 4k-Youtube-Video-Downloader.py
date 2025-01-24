import streamlit as st
import yt_dlp
import io

# Get video information
def get_video_info(url):
    ydl_opts = {
        'quiet': True,
        'cookiefile': 'cookies.txt',  # Optional: Use cookies to bypass restrictions if necessary
    }
    try:
        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
            return ydl.extract_info(url, download=False)
    except Exception as e:
        st.error(f"Error getting video info: {str(e)}")
        return None

# Get quality options
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
        buffer = io.BytesIO()
        ydl_opts = {
            'format': f'{format_id}+bestaudio/best',
            'quiet': True,
            'outtmpl': '-',  # Avoid saving to disk
            'merge_output_format': 'mp4',
        }

        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
            ydl.download([url])
            info = ydl.extract_info(url, download=False)
            return buffer, info["title"]
    except Exception as e:
        st.error(f"Error downloading video: {str(e)}")
        return None, None

# Streamlit UI
st.set_page_config(page_title="YouTube Downloader", page_icon="🎬", layout="centered")
st.title("YouTube Video Downloader 🎥")
st.markdown("### Fetch and download YouTube videos in your preferred quality.")

# Input URL
url = st.text_input("Enter YouTube URL:", placeholder="https://www.youtube.com/watch?v=...")

if url:
    with st.spinner("Fetching video information..."):
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

            if st.button("Download Video"):
                with st.spinner("Downloading video..."):
                    buffer, title = download_video_to_memory(url, format_id)

                if buffer:
                    st.success("Download ready!")
                    st.download_button(
                        label="Click to Download",
                        data=buffer,
                        file_name=f"{title}.mp4",
                        mime="video/mp4"
                    )
                else:
                    st.error("Failed to prepare video for download.")
        else:
            st.error("No quality options available.")
    else:
        st.error("Failed to fetch video information.")

# Footer
st.markdown("---")
st.caption("This project is created by Bibek Kumar Thagunna. Respect copyright laws.")
