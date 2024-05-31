import imaplib
import oauth2
import google.auth.transport.requests

def get_oauth2_token(credentials):
    # Refresca el token de acceso si es necesario
    request = google.auth.transport.requests.Request()
    credentials.refresh(request)
    return credentials.token

def connect_to_gmail_imap(email, oauth2_token):
    imap_host = 'imap.gmail.com'
    imap_port = 993

    mail = imaplib.IMAP4_SSL(imap_host, imap_port)
    auth_string = f'user={email}\1auth=Bearer {oauth2_token}\1\1'
    mail.authenticate('XOAUTH2', lambda x: auth_string)
    return mail

def main():
    email = input("Introduce el correo electrónico: ")

    # Cargar las credenciales
    credentials = oauth2.load_credentials(email)

    # Obtener el token de acceso
    oauth2_token = get_oauth2_token(credentials)

    # Conectarse al servidor IMAP de Gmail
    mail = connect_to_gmail_imap(email, oauth2_token)
    mail.select('inbox')

    # Buscar todos los correos electrónicos en la bandeja de entrada
    result, data = mail.search(None, 'ALL')

    if result == 'OK':
        # Obtener la lista de IDs de correos
        email_ids = data[0].split()
        print(f'Número de correos: {len(email_ids)}')
    else:
        print(f"Error al buscar correos: {result}")

    # Cerrar la conexión
    mail.logout()

if __name__ == '__main__':
    main()
