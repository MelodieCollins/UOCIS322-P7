# Streaming Service 

import os
import itertools
import flask
from flask import Flask, request, jsonify
from flask_restful import Resource, Api
from pymongo import MongoClient
import json
from itsdangerous import (TimedJSONWebSignatureSerializer \
								  as Serializer, BadSignature, \
								  SignatureExpired)
from passlib.apps import custom_app_context as pwd_context
import time


app = Flask(__name__)
api = Api(app)

client = MongoClient('mongodb://' + os.environ['MONGODB_HOSTNAME'], 27017)
db = client.tododb

class listAll(Resource):
	def get(self, dtype='json'):
		items = list(db.brevets.find())
		top = int(request.args.get('top', default='-1').strip())
		open_close = []
		for i in items:
			tmp = [str(i['open']), str(i['close'])]
			open_close.append(tmp)

		if dtype == 'csv':
			return open_close
		x = {
			"List All": open_close
		}
		y = json.dumps(x)
		return y

class listOpenOnly(Resource):
	def get(self, dtype='json'):
		items = list(db.brevets.find())
		top = int(request.args.get('top', default='-1').strip())

		open_only = []
		app.logger.debug(top)
		if top != -1:
			for i in items:
				if len(open_only) < int(top):
					open_only.append(str(i['open']))
		else:
			for i in items:
				app.logger.debug("/"*50)
				app.logger.debug(items)
				app.logger.debug("/"*50)
				app.logger.debug(str(i['open']))
				app.logger.debug("/"*50)
				open_only.append(str(i['open']))

		if dtype == 'csv':
			return open_only
		x = {
			"List Open Only": open_only
		}
		y = json.dumps(x)
		return y

class listCloseOnly(Resource):
	def get(self, dtype='json'):
		items = list(db.brevets.find())
		top = int(request.args.get('top', default='-1').strip())

		close_only = []
		app.logger.debug(top)
		if top != -1:
			for i in items:
				if len(close_only) < int(top):
					close_only.append(str(i['close']))
		else:
			for i in items:
				close_only.append(str(i['close']))

		if dtype == 'csv':
			return close_only
		x = {
			"List Close Only": close_only
		}
		y = json.dumps(x)
		return y

#gives back id, username, and password hash
class getUser(Resource):
	def get(self, username):
		x = db.users.find_one({"username" :username}) #gives back dictionary
		app.logger.debug("="*50)
		app.logger.debug("user: %r",x)
		app.logger.debug("="*50)
		if not x:
			return jsonify({})
		u = {"username": x["username"], "token": x["token"]}
		y = jsonify(u)

		return y


class Token(Resource):
	def get(self, password):
		token = pwd_context.encrypt(password)
		doc = {'token':token}
		app.logger.debug("="*50)
		app.logger.debug("doc: %r", doc)
		app.logger.debug("="*50)
		return jsonify(doc)

class Guess(Resource):
	def get(username, password):
		x = db.users.find_one({"username" : username}) #gives back dictionary
		if not x:
			return jsonify({"result" : False})
		token = pwd_context.encrypt(password)
		doc = {'result' : pwd_context.verify(token, x['token'])}
		app.logger.debug("#"*50)
		app.logger.debug("Guess doc: %r", doc)
		app.logger.debug("#"*50)
		return jsonify(doc)

class Register(Resource):
	def post(self):
		username = request.form.get('username', default='').strip()
		token = request.form.get('token', default='').strip()
		if not username:
			return flask.abort(400, "username is required")
		if not token:
			return flask.abort(400, "token is required")
		if db.users.find_one({"username" :username}):
			return flask.abort(400, "username is taken")
		item_doc = {
                'username': username,
                'token': token
            }
		db.users.insert_one(item_doc) #creates user


# SECRET_KEY = 'hello123#$5!'


# def generate_auth_token(expiration=600):
#    s = Serializer(SECRET_KEY, expires_in=expiration)
#    return s.dumps({'id_':user_id})


# def verify_auth_token(token):
# 	s = Serializer(SECRET_KEY)
# 	try:
# 		data = s.loads(token)
# 	except SignatureExpired:
# 		return "Expired token!"    # valid token, but expired
# 	except BadSignature:
# 		return "Invalid token!"    # invalid token
# 	return f"Success! Welcome {data['username']}."


api.add_resource(listAll, '/listAll/', '/listAll/<dtype>')
api.add_resource(listOpenOnly, '/listOpenOnly/', '/listOpenOnly/<dtype>')
api.add_resource(listCloseOnly, '/listCloseOnly/', '/listCloseOnly/<dtype>')
api.add_resource(getUser, '/getUser/<username>')
api.add_resource(Register, '/register/')
api.add_resource(Token, '/token/<password>')
api.add_resource(Guess, '/guess/<username>/<password>')


if __name__ == '__main__':
	app.run(host='0.0.0.0', debug=True)