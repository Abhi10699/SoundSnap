import requests
import base64
import random
import sqlite3


from transformers import ViltProcessor, ViltForQuestionAnswering
from PIL import Image

processor = ViltProcessor.from_pretrained("dandelin/vilt-b32-finetuned-vqa")
model = ViltForQuestionAnswering.from_pretrained("dandelin/vilt-b32-finetuned-vqa")


def get_conn():
    return sqlite3.connect("./session.db", detect_types=sqlite3.PARSE_DECLTYPES)


# db functions

def setup_db():

    conn = get_conn()
    curr = conn.cursor()
    
    # create table
    
    session_tbl_query = """
    CREATE TABLE IF NOT EXISTS tbl_soundsnap_session(
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        token VARHCHAR(200) NOT NULL,
        created_at DATETIME DEFAULT current_timestamp
    );
    """
    
    curr.execute(session_tbl_query)
    curr.close()
    conn.commit()



def get_session_key():
    conn = get_conn()
    session_fetch_query = """
    SELECT 
        token, 
        (created_at + 36000000 > datetime('now')) as "token_expired" 
    FROM
        tbl_soundsnap_session 
    ORDER BY 
        created_at DESC;
    """
    
    curr = conn.cursor()
    session_details = curr.execute(session_fetch_query)
    row = session_details.fetchone()
    
    session_token = row[0]
    token_expired = True if row[1] == 1 else False
    
    curr.close()
    return session_token,  token_expired    


def update_token(token):
    conn = get_conn()
    session_update_query = f"INSERT INTO tbl_soundsnap_session (token) VALUES ('{token}')"
    curr = conn.cursor()
    curr.execute(session_update_query)
    curr.close()
    conn.commit()

# spotify auth
def authorize_spotify():    
    # fetch new token after 1 hour
    spotify_client = "8322d83619b34791b49d90267051ba22"
    spotify_secret = "0d5ef8411a96443bbe5bb4e3f01958ac"


    auth_api = "https://accounts.spotify.com/api/token"
    buffer = f"{spotify_client}:{spotify_secret}".encode()
    buffer_b64 = base64.standard_b64encode(buffer).decode()
    headers = {
        "Authorization": f"Basic {buffer_b64}",
        "Content-Type": "application/x-www-form-urlencoded"
    }

    request_data = requests.post(auth_api, headers=headers, data={
                                 "grant_type": "client_credentials"})
    if request_data.status_code == 200:
        token_data = request_data.json()
        token = token_data['access_token']
    
        update_token(token)
        return token
    else:
        print("something is wrong")



# machine learning functions

def get_image_from_url(url):
    return Image.open(requests.get(url, stream=True).raw)


def get_image_from_bytes(imageIo):
    return Image.open(imageIo)


def get_image_logits(image, questions):

  # prepare inputs
  encoding = processor(image, questions, return_tensors="pt")

  # forward pass
  outputs = model(**encoding)
  logits = outputs.logits
  idx = logits.argmax(-1).item()
  answer = model.config.id2label[idx]
  return answer



def fetch_playlist_songs(playlist_url, token):

    songs = []
    headers = {
        "Authorization": f"Bearer {token}"
    }
    request_data = requests.get(playlist_url, headers=headers)
    if request_data.status_code == 200:
        request_json = request_data.json()
        playlist_songs = request_json['items']

        for song in playlist_songs:
            track_root = song['track']
            track_name = track_root['name']
            track_uri = track_root['uri']

            track_payload = {"track_uri": track_uri, "track_name": track_name}
            songs.append(track_payload)

    return songs


def fetch_playlists(search_term, token):
    spotify_api = f"https://api.spotify.com/v1/search?q={search_term}&type=playlist"
    headers = {
        "Authorization": f"Bearer {token}"
    }
    request_data = requests.get(spotify_api, headers=headers)

    compiled_songs = []

    if request_data.status_code == 200:
        # decode json
        json_decoded = request_data.json()
        root = json_decoded['playlists']
        playlists = root['items']

        for playlist in playlists[:2]:
            playlist_songs_url = playlist['tracks']['href']
            songs = fetch_playlist_songs(playlist_songs_url, token)
            compiled_songs.extend(songs)

    return compiled_songs



def recommend_songs(image):  
  # question chain
  image = get_image_from_bytes(image)
  image_logits = get_image_logits(image, "what is the activity in this image?")
  
  try:
    spotify_token = authorize_spotify()
    songs = fetch_playlists(image_logits, spotify_token)
    payload = []
    for _ in range(5):
        random_index = random.randrange(len(songs))
        song = songs[random_index]
        track_id = song['track_uri'].split(":")[2]
        payload.append(track_id)

    return payload
  except:
    print("Something went wrong..")