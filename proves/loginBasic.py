import imaplib

# Conectarse al servidor IMAP
mail = imaplib.IMAP4_SSL('imap.gmail.com')

# Autenticarse
email = ''
password = ''
try:
    mail.login(email, password)
    print("Inicio de sesión exitoso.")
except imaplib.IMAP4_SSL.error as e:
    print(f"Error de autenticación: {e}")

# Seleccionar la bandeja de entrada
mail.select('inbox')

# Buscar todos los correos electrónicos en la bandeja de entrada
result, data = mail.search(None, 'ALL')

# Obtener la lista de IDs de correos
email_ids = data[0].split()
print(f'Número de correos: {len(email_ids)}')
