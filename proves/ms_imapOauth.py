import imaplib
import ms_oauth2

def connect_to_outlook_imap(email, oauth2_token):
    imap_host = 'outlook.office365.com'
    imap_port = 993

    mail = imaplib.IMAP4_SSL(imap_host, imap_port)
    auth_string = f'user={email}\1auth=Bearer {oauth2_token}\1\1'
    mail.authenticate('XOAUTH2', lambda x: auth_string)
    return mail

def main():
    email = input("Introduce el correo electrónico: ")

    # Obtener el token de acceso
    oauth2_token = ms_oauth2.get_access_token(email)

    # Conectarse al servidor IMAP de Outlook
    mail = connect_to_outlook_imap(email, oauth2_token)
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
