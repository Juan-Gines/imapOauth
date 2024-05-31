from flask import Flask, redirect, url_for, session, request, jsonify
from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import Flow
from google.auth.transport.requests import Request
import imaplib
import os
import json
import googleapiclient.discovery
from email import message_from_bytes

# Desactivar el requisito de HTTPS en desarrollo
os.environ['OAUTHLIB_INSECURE_TRANSPORT'] = '1'

app = Flask(__name__)
app.secret_key = 'tu_secreto'
CLIENT_SECRETS_FILE = 'credentials.json'
TOKENS_FILE = 'ddbb/go_tokens.json'

SCOPES = ['https://mail.google.com/', 'https://www.googleapis.com/auth/userinfo.email', 'openid']
REDIRECT_URI = 'http://localhost:5000/callback'

flow = Flow.from_client_secrets_file(
    CLIENT_SECRETS_FILE,
    scopes=SCOPES,
    redirect_uri=REDIRECT_URI)

@app.route('/')
def index():
    return 'Welcome to the OAuth2 IMAP email checker!'

@app.route('/authorize')
def authorize():
    authorization_url, state = flow.authorization_url(access_type='offline', include_granted_scopes='true')
    session['state'] = state
    return redirect(authorization_url)

@app.route('/callback')
def callback():
    flow.fetch_token(authorization_response=request.url)

    if not session['state'] == request.args['state']:
        return 'State mismatch', 400

    credentials = flow.credentials

    # Construir el servicio de userinfo con las credenciales
    user_info_service = googleapiclient.discovery.build('oauth2', 'v2', credentials=credentials)

    # Intentar obtener la información del usuario
    try:
        user_info = user_info_service.userinfo().get().execute()
        email = user_info['email']
    except googleapiclient.errors.HttpError as e:
        print(f"Error obtaining user info: {e}")
        return f"Error obtaining user info: {e}"

    token_data = {
        'token': credentials.token,
        'refresh_token': credentials.refresh_token,
        'token_uri': credentials.token_uri,
        'client_id': credentials.client_id,
        'client_secret': credentials.client_secret,
        'scopes': credentials.scopes
    }

    tokens = {}
    if os.path.exists(TOKENS_FILE):
        with open(TOKENS_FILE, 'r') as token_file:
            tokens = json.load(token_file)

    tokens[email] = token_data

    with open(TOKENS_FILE, 'w') as token_file:
        json.dump(tokens, token_file)

    session['token'] = token_data
    session['email'] = email  # Guarda el email en la sesión para accederlo más fácilmente
    return 'Autorització exitosa!'

def get_credentials(email):
    # Verificar si hay un token de sesión almacenado
    if 'token' in session and session.get('email') == email:
        token_data = session['token']
        credentials = Credentials(
            token=token_data['token'],
            refresh_token=token_data['refresh_token'],
            token_uri=token_data['token_uri'],
            client_id=token_data['client_id'],
            client_secret=token_data['client_secret'],
            scopes=token_data['scopes']
        )
        return credentials

    # Si no hay credenciales en la sesión, cargarlas desde el archivo de tokens
    if not os.path.exists(TOKENS_FILE):
        return None

    with open(TOKENS_FILE, 'r') as token_file:
        tokens = json.load(token_file)

    token_data = tokens.get(email)
    if not token_data:
        return None

    credentials = Credentials(
        token=token_data['token'],
        refresh_token=token_data['refresh_token'],
        token_uri=token_data['token_uri'],
        client_id=token_data['client_id'],
        client_secret=token_data['client_secret'],
        scopes=token_data['scopes']
    )

    # Verificar si el token de acceso ha expirado y renovarlo si es necesario
    if credentials.expired and credentials.refresh_token:
        credentials.refresh(Request())
        tokens[email] = {
            'token': credentials.token,
            'refresh_token': credentials.refresh_token,
            'token_uri': credentials.token_uri,
            'client_id': credentials.client_id,
            'client_secret': credentials.client_secret,
            'scopes': credentials.scopes
        }
        with open(TOKENS_FILE, 'w') as token_file:
            json.dump(tokens, token_file)

        # Actualizar sesión con el nuevo token
        session['token'] = tokens[email]

    return credentials

@app.route('/check_email/<email>')
def check_email(email):
    credentials = get_credentials(email)
    if not credentials:
        return redirect(url_for('authorize'))

    # Conectar al servidor IMAP
    imap_host = 'imap.gmail.com'
    impa_port = 993
    imap_conn = imaplib.IMAP4_SSL(imap_host, impa_port)
    imap_conn.debug = 4
    try:
        auth_string = f'user={email}\1auth=Bearer {credentials.token}\1\1'
        imap_conn.authenticate('XOAUTH2', lambda x: auth_string)
    except imaplib.IMAP4.error as e:
        print(f"Authentication failed: {e}")
        return f"Authentication failed: {e}"

    imap_conn.select('inbox')
    status, email_ids = imap_conn.search(None, 'ALL')
    email_details = []
    if status == 'OK':
        email_ids = email_ids[0].split()
        for email_id in email_ids:
            status, msg_data = imap_conn.fetch(email_id, '(RFC822.HEADER)')
            if status == 'OK':
                for response_part in msg_data:
                    if isinstance(response_part, tuple):
                        msg = message_from_bytes(response_part[1])
                        email_details.append({
                            'id': email_id.decode('utf-8'),
                            'subject': msg['subject'],
                        })

    imap_conn.logout()
    return jsonify(email_details)

if __name__ == '__main__':
    app.run('localhost', 5000, debug=True)
