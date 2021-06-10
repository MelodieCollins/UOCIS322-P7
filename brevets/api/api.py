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
import time


app = Flask(__name__)
api = Api(app)

client = MongoClient('mongodb://' + os.environ['MONGODB_HOSTNAME'], 27017)
db = client.tododb

class listAll(Resource):
	def get(self, dtype='json'):
		items = list(db.tododb.find())
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
		items = list(db.tododb.find())
		top = int(request.args.get('top', default='-1').strip())

		open_only = []
		app.logger.debug(top)
		if top != -1:
			for i in items:
				if len(open_only) < int(top):
					open_only.append(str(i['open']))
		else:
			for i in items:
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
		items = list(db.tododb.find())
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
		x = db.tododb.find_one({"username" :username}) #gives back dictionary
		app.logger.debug("="*50)
		app.logger.debug(x)
		app.logger.debug("="*50)
		if not x:
			return jsonify({})
		u = {"username": x["username"], "token": x["token"]}
		y = jsonify(u)

		return y

class createUser(Resource):
	def post(self):
		username = request.form.get('username', default='').strip()
		token = request.form.get('token', default='').strip()
		if not username:
			return flask.abort(400, "username is required")
		if not token:
			return flask.abort(400, "token is required")
		if db.tododb.find_one({"username" :username}):
			return flask.abort(400, "username is taken")
		item_doc = {
                'username': username,
                'token': token
            }
		db.tododb.insert_one(item_doc) #creates user


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
api.add_resource(createUser, '/createUser/')


if __name__ == '__main__':
	app.run(host='0.0.0.0', debug=True)