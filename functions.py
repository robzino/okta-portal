
from flask import Flask, redirect, url_for, request, render_template, session, logging
from flask_session.__init__ import Session
import json,os,sys, random, string, re, logging, time, datetime, requests


app = Flask(__name__)
app.config['SESSION_TYPE'] = 'filesystem'
app.config['SECRET_KEY'] = 'asjhd4895647664745464138537262ds00cd'
sess = Session()

gunicorn_logger = logging.getLogger('gunicorn.error')
app.logger.handlers = gunicorn_logger.handlers
app.logger.setLevel(gunicorn_logger.level)

###########################################################################
# other functions

def gen_guid(size=6, chars=string.ascii_lowercase + string.digits):
	return ''.join(random.choice(chars) for x in range(size))

def format_date(inbound_str):
	tmpstr = inbound_str.replace("T", " ")
	tmpstr2 = tmpstr.replace(".000Z", "")
	return tmpstr2

def check_admin_role(role_data):
	admin_bool='n'
	for i in range(0, len(role_data)):
		tmpstr = role_data[i]['label']
		if 'Administrator' in tmpstr:
			admin_bool='y'
	return admin_bool

def log_msg(oidc, msg):
	email = oidc.user_getfield('email')
	ip=request.environ.get('HTTP_X_REAL_IP', request.remote_addr)
	app.logger.info(email + " : " + ip + " : " + msg)
