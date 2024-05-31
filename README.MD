#Projecte per Nan-Tic conectar als emails de clients

El projecte consisteix en fer una conexió per IMAP + autentificació Oauth2. S'ha de fer per gmail i per outlook.

## Contingut del projecte

El projecte te una carpeta proves que te archius que es conecten a mails de diferentes maneres.

Y els archius importants que son:

- server.py: conté el servidor per els emails de gmail
- ms_server.py: conté el servidor per els emails de outlook

## Instalació del projecte

- Primer creem l'entorn del projecte amb les seves llibreries.
~~~
python -m venv myenv
~~~
- Activar l' entorn virtual
~~~
# En Windows
.\myenv\Scripts\activate

# En macOS/Linux
source myenv/bin/activate
~~~
- Instalar les llibreries
~~~
pip install -r requirements.txt
~~~

Ja ho tenim tot instalat.

## Configuració del outlook de microsoft

1. Registrem una aplicació en Azure:

- Entrem al Azure Portal i navegem fins a microsoft openid.
- Selecciona app registrations -> + new registration.
- Posali nom i scull acounts organizationals i personals.
- Escriu la url Redirect URI 'http://localhost:5000/callback'.

2. Configurem permisos API:

- Navega a API permissions.
- Agrega permisos, escull microsoft graph.
- Necessitem 'User.Read IMAP.AccessAsUser.All Mail.Read'. Respectivament son per obtenir info del usuari, acces al email i llegir emails.

3. Codi secret del client

- Navegem fins a certificates & secrets.
- Cliquem a '+ New client secret'.
- Guardem la informacío en un archiu json anomenat 'ms_credentials.json', ho has de guardar al moment perque quant tanquis la pantalla el número 'client_secret(value)' no el mostrará de nou.
~~~
{
    "CLIENT_ID": "El client id",
    "CLIENT_SECRET": "El secret del client",
    "REDIRECT_URI": "http://localhost:5000/callback"
}
~~~
Amb aixó ya estará configurat el outlook.

## Configuració del Gmail

1. Configurar el projecte a Google

- Ves-hi a google cloud console.
- Crea un nou projecte.

2. Habilitem Gmail Api

- Navega a 'apis y servicios'.
- Habilitem la 'gmail api'.

3. Donem permissos a la Api

- A 'Oauth consent screen':
    - Escollim 'User Type: External'.
    - Emplenem el registre de la app.
    - Agregem permisos 'https://mail.google.com/', 'auth/userinfo.email' i 'openid'

4. Crearem les credentials pel prokecte

- Anirem a Credentials, crearem les credencials Oauth2 i guardem el archiu al nostre projecte.

Ara ja tenim configurat Gmail.

## Funcionament i endpoints dels servidors

Començarem al ms_server.py per outlook.Url 'localhost:5000' Llistat d'endpoints

- '/' : info de la app.
- '/login': Et redirecciona a la url de autentificacio de outlook.
- '/callback': Recull el token de outlook, el guarda al array 'ddbb/ms_tokens.json' i a la cookie de session.
- '/test-auth/<email>': busca el token a la cookie de session, després a ms_tokens_json. Si la troba en retornará un llistat amb els mails. Si no la troba ens redirigeix a '/login'

Continuarem amb el server.py per Gmail a la mateixa Url. Llistat d'endpoints:

- '/' : info de la app.
- '/authorize': Et redirecciona a la url de autentificacio de gmail.
- '/callback': Recull el token de gmail, el guarda al array 'ddbb/go_tokens.json' i a la cookie de session.
- '/check_email/<email>': busca el token a la cookie de session, després a go_tokens_json. Si la troba en retornará un llistat amb els mails. Si no la troba ens redirigeix a '/authorize'.

## Agraïments

Gràcies a Nan-Tic per el suport.
