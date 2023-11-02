import streamlit as st
import streamlit.components.v1 as components
from funcs import setup_db, recommend_songs

st.title("SoundSnap 🎵")


with st.spinner("Setting Up Database.."):
  setup_db()

st.success("Daabase Setup Complete", icon="✅")


# upload image
image_file = st.file_uploader(
  "Upload Image", 
  accept_multiple_files=False, 
)


if image_file:
  songs = recommend_songs(image_file) 
  col1, col2 = st.columns(2)

  with col1:
    st.image(image_file)

  with col2:
    for song_id in songs:
      components.html(
        f"""
        <iframe 
          style="border-radius:12px" 
          src="https://open.spotify.com/embed/track/{song_id}?utm_source=generator" 
          width="100%"
          height="190"
          frameBorder="0" 
          allowfullscreen="" 
          allow="autoplay; 
          clipboard-write; 
          encrypted-media; 
          fullscreen; 
          picture-in-picture" 
          loading="lazy">
        </iframe>
        """,
        height=200
      )