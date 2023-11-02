import streamlit as st
import streamlit.components.v1 as components
from funcs import setup_db, recommend_songs

st.title("SoundSnap 🎵")
st.write("Discover music through your photos with SoundSnap. Snap a picture, and we'll create personalized playlists to match the ambiance of your images. Explore a new way of finding music that resonates with your moments.")



with st.spinner("Setting Up Database.."):
  setup_db()


# upload image
image_file = st.file_uploader(
  "Upload Image", 
  accept_multiple_files=False, 
  type=['png', 'jpg',"jpeg"] 
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