# app.py
from flask import Flask, render_template, redirect, request, session, url_for, jsonify
import spotipy
from spotipy.oauth2 import SpotifyOAuth
from config import SPOTIPY_CLIENT_ID, SPOTIPY_CLIENT_SECRET

app = Flask(__name__)
app.secret_key = 'giuyyugj'  # Cambia esto por una clave secreta segura

# Configuración del cliente de Spotify
sp_oauth = SpotifyOAuth(
    client_id=SPOTIPY_CLIENT_ID,
    client_secret=SPOTIPY_CLIENT_SECRET,
    redirect_uri='http://127.0.0.1:5000/callback',
    scope='user-modify-playback-state',
)

@app.route('/')
def index():
    access_token = session.get('access_token')
    if not access_token:
        return redirect(url_for('login'))
    return render_template('index.html')

@app.route('/login')
def login():
    auth_url = sp_oauth.get_authorize_url()
    return redirect(auth_url)

@app.route('/callback')
def callback():
    session.clear()
    code = request.args.get('code')
    token_info = sp_oauth.get_access_token(code)
    session['access_token'] = token_info['access_token']
    return redirect(url_for('search_song'))

@app.route('/search', methods=['GET', 'POST'])
def search_song():
    access_token = session.get('access_token')
    if not access_token:
        return redirect(url_for('login'))

    if request.method == 'POST':
        song_name = request.form.get('song_name')
        if song_name:
            # Realizar búsqueda de canciones en Spotify
            sp = spotipy.Spotify(auth=access_token)
            results = sp.search(q=song_name, type='track')
            songs = results['tracks']['items']
        else:
            songs = []
        return render_template('results.html', songs=songs)
    else:
        return render_template('index.html')

@app.route('/enqueue', methods=['POST'])
def enqueue_song():
    access_token = session.get('access_token')
    print(access_token)
    if not access_token:
        return redirect(url_for('login'))

    sp = spotipy.Spotify(auth_manager=sp_oauth)
    song_uri = request.form.get('song_uri')
    if song_uri:
        sp.add_to_queue(uri=song_uri)
        return redirect(url_for('search_song'))
    else:
        return 'No se pudo encolar la canción.'

@app.route('/api/token', methods=['GET'])
def getToken():
    access_token = session.get('access_token')
    return jsonify({"token": access_token})

if __name__ == '__main__':
    app.run(debug=True)
