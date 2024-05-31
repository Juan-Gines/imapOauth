from flask import Flask, jsonify, redirect, request, session
import requests
import json
import os

app = Flask(__name__)
app.secret_key = 'secret_key'

CREDENTIALS_FILE = 'ms_credentials.json'
with open(CREDENTIALS_FILE, 'r') as f:
    credentials = json.load(f)

CLIENT_ID = credentials['CLIENT_ID']
CLIENT_SECRET = credentials['CLIENT_SECRET']
REDIRECT_URI = credentials['REDIRECT_URI']
AUTH_URL = 'https://login.microsoftonline.com/common/oauth2/v2.0/authorize'
TOKEN_URL = 'https://login.microsoftonline.com/common/oauth2/v2.0/token'
SCOPE = 'User.Read IMAP.AccessAsUser.All Mail.Read'
TOKEN_FILE = 'ddbb/ms_tokens.json'

def load_tokens():
    if os.path.exists(TOKEN_FILE):
        with open(TOKEN_FILE, 'r') as f:
            return json.load(f)
    return {}

def save_tokens(tokens):
    with open(TOKEN_FILE, 'w') as f:
        json.dump(tokens, f)

def getCredentials(email):
    if 'access_token' in session:
        return session['access_token']
    if email:
        tokens_db = load_tokens()
        if email in tokens_db:
            session['access_token'] = tokens_db[email]
            return tokens_db[email]
    return None
def get_user_email(access_token):
    headers = {
        'Authorization': f'Bearer {access_token}',
        'Accept': 'application/json'
    }
    response = requests.get('https://graph.microsoft.com/v1.0/me', headers=headers)
    user_info = response.json()
    return user_info.get('mail')

def get_user_emails(access_token):
    headers = {
        'Authorization': f'Bearer {access_token}',
        'Accept': 'application/json'
    }
    response = requests.get('https://graph.microsoft.com/v1.0/me/messages', headers=headers)
    if response.status_code == 200:
        messages = response.json().get('value', [])
        email_data = [{'id': msg['id'], 'subject': msg['subject']} for msg in messages]
        return email_data
    else:
        print(f"Error al obtener mensajes: {response.text}")
        return []

@app.route('/')
def home():
    return 'Bienvenido a la aplicación de autenticación OAuth2 con IMAP'

@app.route('/login')
def login():
    auth_url = f'{AUTH_URL}?client_id={CLIENT_ID}&response_type=code&redirect_uri={REDIRECT_URI}&response_mode=query&scope={SCOPE}'
    return redirect(auth_url)

@app.route('/callback')
def callback():
    code = request.args.get('code')
    data = {
        'client_id': CLIENT_ID,
        'client_secret': CLIENT_SECRET,
        'grant_type': 'authorization_code',
        'code': code,
        'redirect_uri': REDIRECT_URI,
        'scope': SCOPE
    }
    response = requests.post(TOKEN_URL, data=data)
    tokens = response.json()
    session['access_token'] = tokens['access_token']
    # Obtener el correo electrónico del usuario
    user_email = get_user_email(tokens['access_token'])
    session['user_email'] = user_email

    # Guardar token con el correo electrónico del usuario como identificador
    tokens_db = load_tokens()
    tokens_db[user_email] = tokens['access_token']
    save_tokens(tokens_db)

    return 'Autenticación exitosa'

@app.route('/test-auth/<email>')
def test_auth(email):
    access_token = getCredentials(email)
    if not access_token:
        return redirect('/login')
    emails = get_user_emails(access_token)
    return jsonify({'user_email': email, 'emails': emails})

if __name__ == '__main__':
    app.run(debug=True)
