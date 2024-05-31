import json
import os
import requests
from msal import ConfidentialClientApplication

# Configuración

CREDENTIALS_FILE = 'ms_credentials.json'
with open(CREDENTIALS_FILE, 'r') as f:
    credentials = json.load(f)

CLIENT_ID = credentials['CLIENT_ID']
CLIENT_SECRET = credentials['CLIENT_SECRET']
REDIRECT_URI = credentials['REDIRECT_URI']
TENANT_ID = credentials['TENANT_ID']
AUTHORITY = f'https://login.microsoftonline.com/{TENANT_ID}'
REDIRECT_URI = 'http://localhost'
SCOPES = ['https://outlook.office365.com/IMAP.AccessAsUser.All']
TOKEN_FILE = 'ddbb/ms_tokens.json'

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
    tokens = [t for t in tokens if t['email'] != email]  # Elimina el token existente
    tokens.append({'email': email, 'token': token})  # Agrega el nuevo token
    save_tokens(tokens)

def authenticate(email):
    app = ConfidentialClientApplication(
        CLIENT_ID,
        authority=AUTHORITY,
        client_credential=CLIENT_SECRET,
    )

    # Cargar token desde archivo
    token_data = get_token_for_email(email)
    if token_data and 'refresh_token' in token_data:
        result = app.acquire_token_by_refresh_token(token_data['refresh_token'], SCOPES)
        if 'access_token' in result:
            save_token_for_email(email, result)
            return result

    # Autenticar y obtener nuevo token
    flow = app.initiate_auth_code_flow(scopes=SCOPES)
    result = app.acquire_token_by_auth_code_flow(flow)

    if 'access_token' in result:
        save_token_for_email(email, result)
        return result
    else:
        raise Exception(f"Error en la autenticación: {result.get('error_description')}")

def get_access_token(email):
    token_data = authenticate(email)
    return token_data['access_token']

if __name__ == '__main__':
    email = input("Introduce el correo electrónico: ")
    access_token = get_access_token(email)
    print("Autenticación exitosa. Token de acceso obtenido.")
