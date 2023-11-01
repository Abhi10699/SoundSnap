import streamlit as st
# from funcs import setup_db, recommend_songs

# setup_db()
st.title("SoundSnap 🎵")

# upload image
image_file = st.file_uploader(
  "Upload Image", 
  accept_multiple_files=False, 
  type=["image/png", "image/jpg", "image/jpeg", "image/webp"]
)


if image_file:
  pass
  # recommend_songs(image_file)