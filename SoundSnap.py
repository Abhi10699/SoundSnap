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
  type=["image/png", "image/jpg", "image/jpeg", "image/webp"]
)


if image_file:
  songs = recommend_songs(image_file) 
  for song_id in songs:
    components.iframe(
      f"""
      <iframe 
        style="border-radius:12px" 
        src="https://open.spotify.com/embed/track/{song_id}?utm_source=generator" 
        width="100%" height="352" 
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
      height=352
    )