# app.py
from flask import Flask, render_template, redirect, request, session, url_for, jsonify
import requests
import spotipy
from spotipy.oauth2 import SpotifyOAuth
from config import SPOTIPY_CLIENT_ID, SPOTIPY_CLIENT_SECRET

app = Flask(__name__)
app.secret_key = 'giuyyugj'  # Cambia esto por una clave secreta segura


@app.route('/')
def index():
    session.clear()
    access_token = session.get('sp_token')
    if not access_token:
        return redirect(url_for('login'))
    return render_template('index.html')

@app.route('/buscar')
def buscar():
    return render_template('borrar.html')

@app.route('/login')
def login():
    url = 'http://rocolaserver.azurewebsites.net/api/token'
    response = requests.get(url)
    if response.status_code == 200:
        # Obtener el atributo "token" del JSON recibido
        data = response.json()
        token = data.get('token', None)
        print(response.json())
        if token:        
            session['sp_token']=data['token'] 
            return redirect(url_for('search_song'))
        else:
            return jsonify({'error': 'No se encontró el atributo "token" en la respuesta'}), 500
    else:
        return jsonify({'error': 'Error al obtener el token'}), response.status_code

@app.route('/search', methods=['GET', 'POST'])
def search_song():
    access_token = session.get('sp_token')
    if not access_token:
        return redirect(url_for('login'))

    if request.method == 'POST':
        song_name = request.form.get('song_name')
        if song_name:
            try:
                sp = spotipy.Spotify(auth=access_token)
                results = sp.search(q=song_name, type='track')
                songs = results['tracks']['items']
            except:
                print("token expirado")
                return redirect(url_for('loginerror'))
        else:
            songs = []
        return render_template('results.html', songs=songs)
    else:
        return render_template('index.html')

@app.route('/enqueue', methods=['POST'])
def enqueue_song():
    access_token = session.get('sp_token')
    print(access_token)
    if not access_token:
        return redirect(url_for('login'))

    sp = spotipy.Spotify(auth=access_token)
    song_uri = request.form.get('song_uri')
    if song_uri:
        sp.add_to_queue(uri=song_uri)
        return redirect(url_for('search_song'))
    else:
        return 'No se pudo encolar la canción.'
    
@app.route('/loginerror')
def loginerror():
    return render_template('error.html')

if __name__ == '__main__':
    app.run(port=5000,debug=True)