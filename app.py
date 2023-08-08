#
#
from flask import Flask, g, redirect, url_for, request, render_template, session, logging
from flask_session.__init__ import Session
from flask import request
from os import environ
import functions
import json,os,sys, random, string, re, logging, time, datetime, requests
from flask import Flask
from flask_sslify import SSLify
from flask_oidc import OpenIDConnect
from itsdangerous.url_safe import URLSafeTimedSerializer as Serializer
from okta import UsersClient
from oauth2client.client import OAuth2Credentials

# add 2 lines to turn on SSL on
import functools
url_for = functools.partial(url_for, _scheme='https')


app = Flask(__name__)
#sslify = SSLify(app)
app.config['VERSION'] = '2.0b'
app.config['SESSION_TYPE'] = 'filesystem'
app.config['SECRET_KEY'] = 'asjhd4895647664745464138537262ds00cd'

app.config['OIDC_CLIENT_SECRETS'] = 'client_secrets.json'
app.config['OIDC_COOKIE_SECURE'] = False
app.config['OIDC_CALLBACK_ROUTE'] = '/oidc/callback'
app.config['OIDC_SCOPES'] = ['openid', 'email', 'profile']
oidc = OpenIDConnect(app)

sess = Session()

#SSL
#app.config['PREFERRED_URL_SCHEME'] = 'https'

gunicorn_logger = logging.getLogger('gunicorn.error')
app.logger.handlers = gunicorn_logger.handlers
app.logger.setLevel(gunicorn_logger.level)

try:
	OKTA_TOKEN = os.environ.get('TOKEN')
	OKTA_URLBASE = os.environ.get("URLBASE")
	app.config['OKTA_URLBASE'] = OKTA_URLBASE
except:
	functions.log_msg(oidc, 'ENV vars are not set!')


# main routes
@app.route('/')
def home():
	if not oidc.user_loggedin:
		session['user_loggedin'] = ""
	return render_template('home.html')

@app.route('/panel')
@oidc.require_login
def panel():
	if oidc.user_loggedin:
		if session['user_loggedin'] == "":
			functions.log_msg(oidc, "User Logged in")
		session['user_loggedin'] = "yes"
		return render_template('panel.html')
	else:
		session['user_loggedin'] = ""
		return render_template('home.html')

@app.route('/users/search/<pattern>')
def show_users(pattern):
	if not oidc.user_loggedin:
		session['user_loggedin'] = ""
		return render_template('home.html')

	if pattern == "disabled":
		user_data = get_disabled_users()
		session['pattern'] = "disabled"
	else:
		user_data = get_users(pattern)
		session['pattern'] = pattern
		functions.log_msg(oidc, "Showing users for: " + pattern)

	return render_template('users.html',  user_data=user_data)


@app.route('/logout')
def logout():
	oidc.logout()
	session['user_loggedin'] = ""
	return render_template('home.html')


@app.route('/delfactor/<userid>/<factorid>',methods=['GET'])
def factordelete(userid, factorid):
	if userid and factorid:
		url = OKTA_URLBASE + '/api/v1/users/' + userid + '/factors/' + factorid
		res = call_okta('delete', url)
		return redirect('/users/' + userid + '/view?param=factordel')  # go back
	else:
		return render_template('panel.html')

@app.route('/users/<userid>/<action>',methods=['GET', 'POST'])
def useractions(userid, action):
	try:
		param = request.args.get('param', None)
	except:
		param=""

	if not oidc.user_loggedin:
		session['user_loggedin'] = ""
		return render_template('home.html')

	if action == 'view':
		user_data = get_user(userid)
		if user_data == 'err':
			return redirect('/panel')  # go back

		session['custemail'] = user_data['profile']['email']
		factor_data = get_user_factors(userid)
		role_data = get_user_roles(userid)
		if role_data != 'err':
			admin_bool=functions.check_admin_role(role_data)
			return render_template('showuser.html', factor_data=factor_data, pattern=session['pattern'], admin_bool=admin_bool, param=param, user_data=user_data)
		else:
			return render_template('panel.html', msg="Role API call failed.")

	if action == 'edit':
		user_data = get_user(userid)
		if user_data == 'err':
			return redirect('/panel')  # go back

		return render_template('edituser.html', user_data=user_data)


	if action == 'deactivate':
		update_user_status(userid, 'deactivate')
		update_user_status(userid, 'reset_factors')
		return redirect('/users/' + userid + '/view?param=deactivate')  # go back

	if action == 'activate':
		update_user_status(userid, 'activate')
		return redirect('/users/' + userid + '/view?param=activate')  # go back

	if action == 'delete':
		res=delete_user(userid)
		if res == 'err':
			return render_template('panel.html', msg="Delete action failed.")
		else:
			return render_template('panel.html', msg="User was deleted.")

	if action == 'reset':
		update_user_status(userid, 'reset_password?sendEmail=true')
		return redirect('/users/' + userid + '/view?param=reset')  # go back

	if action == 'unlock':
		update_user_status(userid, 'unlock')
		return redirect('/users/' + userid + '/view?param=unlock')  # go back

	if action == 'save':
		if request.method == 'POST':
			fname = request.form['fname']
			lname = request.form['lname']
			mobile = request.form['mobile']
			if fname and lname and mobile:
				res=update_user(userid, fname, lname, mobile)

		return redirect('/users/' + userid + '/view?param=save')  # go back


@app.route('/user/search/submit',methods = ['POST'])
def searchsubmit_result():
	if request.method == 'POST':
		pattern = request.form['pattern']
		try:
			disabled_cb = request.form['disabled_cb']
		except:
			disabled_cb=""

		if disabled_cb:
			pattern="disabled"

		if pattern:
			return redirect('/users/search/' + pattern)  # show users

		return redirect('/panel')  # go back

###########################################################################
# Base functions

def get_users(pattern):
	url = OKTA_URLBASE + '/api/v1/users?q=' + pattern + '&limit=100'
	res = call_okta('get', url)
	return(res)

def get_disabled_users():
	url = OKTA_URLBASE + '/api/v1/users?filter=status%20eq%20"DEPROVISIONED"'
	res = call_okta('get', url)
	return(res)

def get_user(userid):
	url = OKTA_URLBASE + '/api/v1/users/' + userid
	res = call_okta('get', url)
	return(res)

def get_user_roles(userid):
	url = OKTA_URLBASE + '/api/v1/users/' + userid + '/roles'
	res = call_okta('get', url)
	return(res)

def get_user_factors(userid):
	url = OKTA_URLBASE + '/api/v1/users/' + userid + '/factors'
	res = call_okta('get', url)
	return(res)

def delete_user(userid):
	url = OKTA_URLBASE + '/api/v1/users/' + userid
	res = call_okta('delete', url)
	functions.log_msg(oidc, "Deleted user: " + session['custemail'])
	return(res)


def update_user(userid, fname, lname, phone):
	url = OKTA_URLBASE + '/api/v1/users/' + userid
	data = {
		"profile": {
		"firstName": fname,
		"lastName": lname,
		"mobilePhone": phone
		}
	}
	res = call_okta('post', url, json.dumps(data))
	functions.log_msg(oidc, "Updated information for user: " + session['custemail'])
	return(res)


def update_user_status(userid, action):
	url = OKTA_URLBASE + '/api/v1/users/' + userid + '/lifecycle/' + action
	res = call_okta('post', url)
	functions.log_msg(oidc, "Updated user: " + session['custemail'] + " to status: " + action)
	return(res)


def call_okta(action, url, data=""):
	headers = {'Content-type': 'application/json', 'Accept': 'application/json', 'Authorization': 'SSWS ' + OKTA_TOKEN}
	try:
		if action == 'get':
			result = requests.get(url, data=data, headers=headers)
		if action == 'post':
			result = requests.post(url, data=data, headers=headers)
		if action == 'delete':
			result = requests.delete(url, data=data, headers=headers)

		result.raise_for_status()
		if action == 'delete':
			return('ok')

		parsed_json = json.loads(result.text)
		return(parsed_json)
	except requests.exceptions.HTTPError as errh:
		parsed_json = json.loads(result.text)
		functions.log_msg(oidc, "call_okta error: " + parsed_json['errorSummary'])
		return('err')



###########################################################################
# run the APP

if __name__ == '__main__':
	app.run(debug=False,host='0.0.0.0')
