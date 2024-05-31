import os
import json
import google.auth.transport.requests
import google_auth_oauthlib.flow
import google.oauth2.credentials

# Configuración
CLIENT_SECRET_FILE = 'credentials.json'
SCOPES = ['https://mail.google.com/']
TOKEN_FILE = 'ddbb/go_tokens.json'

def load_tokens():
    if os.path.exists(TOKEN_FILE):
        with open(TOKEN_FILE, 'r') as token_file:
            return json.load(token_file)
    return []

def save_tokens(tokens):
    with open(TOKEN_FILE, 'w') as token_file:
        json.dump(tokens, token_file, indent=4)

def get_token_for_email(email):
    tokens = load_tokens()
    for token in tokens:
        if token['email'] == email:
            return token
    return None

def save_token_for_email(email, token):
    tokens = load_tokens()
    # Borrar token antiguo si existe
    tokens = [t for t in tokens if t['email'] != email]
    # Agregar el nuevo token
    tokens.append({'email': email, 'token': token})
    save_tokens(tokens)

def authenticate(email):
    # Cargar las credenciales
    flow = google_auth_oauthlib.flow.InstalledAppFlow.from_client_secrets_file(CLIENT_SECRET_FILE, SCOPES)
    credentials = flow.run_local_server(port=0)

    # Guardar las credenciales en el archivo para usarlas más tarde
    save_token_for_email(email, credentials.to_json())

    return credentials

def load_credentials(email):
    token_info = get_token_for_email(email)
    credentials = None

    if token_info:
        token_data = token_info['token']
        credentials = google.oauth2.credentials.Credentials.from_authorized_user_info(json.loads(token_data), SCOPES)

    if not credentials or not credentials.valid:
        if credentials and credentials.expired and credentials.refresh_token:
            credentials.refresh(google.auth.transport.requests.Request())
        else:
            credentials = authenticate(email)

    return credentials

if __name__ == '__main__':
    email = input("Introduce el correo electrónico: ")
    credentials = load_credentials(email)
    print("Autenticación exitosa. Token de acceso obtenido.")
