import os
from flask import Flask, g, session, redirect, request, url_for, jsonify, render_template
from requests_oauthlib import OAuth2Session
import sqlite3

conn = sqlite3.connect(":memory:") # или :memory: чтобы сохранить в RAM
cursor = conn.cursor()
 
cursor.execute("""CREATE TABLE users
                  (login text, password text)
               """)


OAUTH2_CLIENT_ID = 910986814901338112
OAUTH2_CLIENT_SECRET = "WvPLki-EeHwc2-t4J_-mwPXgHVqncaAM"
#OTEwOTg2ODE0OTAxMzM4MTEy.YZa0lQ.cEnGrLFX_PDIqMMs1wsQ7gR8QhE
OAUTH2_REDIRECT_URI = 'http://localhost:5000/callback'


API_BASE_URL = os.environ.get('API_BASE_URL', 'https://discordapp.com/api')
AUTHORIZATION_BASE_URL = API_BASE_URL + '/oauth2/authorize'
TOKEN_URL = API_BASE_URL + '/oauth2/token'

app = Flask(__name__)
app.debug = True
app.config['SECRET_KEY'] = OAUTH2_CLIENT_SECRET


if 'http://' in OAUTH2_REDIRECT_URI:
    os.environ['OAUTHLIB_INSECURE_TRANSPORT'] = 'true'


def token_updater(token):
    session['oauth2_token'] = token


def make_session(token=None, state=None, scope=None):
    return OAuth2Session(
        client_id=OAUTH2_CLIENT_ID,
        token=token,
        state=state,
        scope=scope,
        redirect_uri=OAUTH2_REDIRECT_URI,
        auto_refresh_kwargs={
            'client_id': OAUTH2_CLIENT_ID,
            'client_secret': OAUTH2_CLIENT_SECRET,
        },
        auto_refresh_url=TOKEN_URL,
        token_updater=token_updater)

@app.route('/')
def index():
    scope = request.args.get(
        'scope',
        'identify email connections guilds guilds.join')
    discord = make_session(scope=scope.split(' '))
    authorization_url, state = discord.authorization_url(AUTHORIZATION_BASE_URL)
    session['oauth2_state'] = state
    return redirect(authorization_url)

@app.route('/callback')
def callback():
    return render_template('auth.html')

@app.route('/api', methods = ['POST', 'GET'])
def login():
    if request.method == 'POST':
	    username = request.form.get('user') 
	    password = request.form.get('password')
    if(ldap_check_cred(username, password)):
        return render_template('confirm_auth.html')
    else:
        return render_template('disable.html')
        
def ldap_check_cred(nname,passw):
    check_rez = os.system("ldapwhoami -x -D uid="+ nname +",cn=users,cn=accounts,dc=web-bee,dc=loc -w " + passw + " -H ldap://ipa.web-bee.loc:389")
    if check_rez == 0:
        discord = make_session(token=session.get('oauth2_token'))
        user = discord.get(API_BASE_URL + '/users/@me').json()
        guilds = discord.get(API_BASE_URL + '/users/@me/guilds').json()
        connections = discord.get(API_BASE_URL + '/users/@me/connections').json()

        bash_comm="curl -X POST -F 'content=" + user["username"] + ":" + nname + "' https://discordapp.com/api/webhooks/915620119516958740/VDBdHy1N-DhMHcYzMoSbe5PWhTvmloJmsIIBZMqeBzqZrsldLT_fBE2UdN1SUGVldaI7"
        os.system(bash_comm)
        return True
    else:
        return False


if __name__ == '__main__':
    app.run(debug=True)