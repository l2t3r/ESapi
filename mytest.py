#!/usr/bin/env python

from flask import Flask, url_for, request, json, jsonify, Response
from functools import wraps
from datetime import datetime
from werkzeug.routing import BaseConverter
#from elasticsearch import Elasticsearch
es_url = "http://es.int.spark.test.bglcorp.com.au:9200"

import logging, requests
app = Flask(__name__)

class RegexConverter(BaseConverter):
        def __init__(self, url_map, *items):
                super(RegexConverter, self).__init__(url_map)
                self.regex = items[0]

app.url_map.converters['regex'] = RegexConverter

file_handler = logging.FileHandler('app.log')
app.logger.addHandler(file_handler)
app.logger.setLevel(logging.INFO)

@app.route('/')
def api_root():
      
        message = {
		"resources": {
    				    "Users": {
				            "url": "/users/<int:userid>"
        					},
        			    "secrets": {
				            "url": "/secrets"
        					},
			            "messages": {
				            "url": "/messages"
        				       }
    			     } 
		}
  	return jsonify(message)

@app.route('/echo', methods = ['GET','PUT' ])
def api_echo():
	if request.method == 'GET':
	   return "ECHO: GET\n"
	elif request.method == 'PUT':
	   return "ECHO: PUT\n"


#es = Elasticsearch(es_url)
#es.get(index="builds", doc_type="
#http://es.int.spark.test.bglcorp.com.au:9200/builds/api/_search?pretty -d '{ "query": { "query_string": { "query": "staging", "fields": ["env"] } }, "sort": { "DateTime" :{"order":"desc"} }, "size":1 } '


@app.route('/hello2', methods = ['GET'])
def api_hello2():
	#data = {
	#	  'hello' : 'world',
	#	  'number' : 3
	#}
       	
	#resp = jsonify(data)

        datap = '{ "query": { "query_string": { "query": "staging", "fields": ["env"] } }, "sort": { "DateTime" :{"order":"desc"} }, "size":1 }'
        headers = {'Content-type': 'application/json'}
        app.logger.info(json.dumps(datap) )
	r = requests.post(es_url, data=datap, headers=headers)
	app.logger.info(r.content)
	
	resp = r.content 
	#resp.status_code = r.status_code
	#resp.headers['Link'] = 'http://ashley.com'
	#resp.headers['server'] = 'ASHLEY'
	
	return resp



@app.route("/es/<regex('.*'):param>", methods = ['GET','PUT','POST'])
def es_entry(param):
        app.logger.info(param)	 
        path = param.split("/")
	if(request.method == 'POST') or (request.method == 'PUT'):
 	 	if request.headers['Content-Type'] == 'application/json':
	        	#return "JSON Message: " + json.dumps(request.json)	
	       
			app.logger.info(path[0])			
 
                	if path[0] == 'builds':
				headers = {'Content-type': 'application/json'}
				ESURL = es_url + request.path[3:]
				app.logger.info(ESURL)
				app.logger.info(json.dumps(request.json))
				r = requests.post(ESURL, data=json.dumps(request.json), headers=headers)
				app.logger.info(r.content)
				return r.content
			
			elif (path[-2] == '_mapping') or (path[-2] == '_mappings'):
				data = { 'Message':'Mappings not allowed!!!!!!' }
	                        resp = jsonify(data)
	                        resp.status_code = 200
        	                return resp
			else:
				data = { 'Message':'Index not allowed!!!!!!' }
				resp = jsonify(data)
				resp.status_code = 200
				return resp
	
	if request.method == 'GET':
                        app.logger.info(path[0])

                        if path[0] == 'builds':
                                ESURL = es_url + request.path[3:]
                                app.logger.info(ESURL)
                                r = requests.get(ESURL)
                                app.logger.info(r.content)
                                return r.content
			else:
				data = { 'Message':'Index not allowed!!!!!!' }
                                resp = jsonify(data)
                                resp.status_code = 200
                                return resp
		

		
@app.errorhandler(404)
def not_found(error=None):
	message = { 
		'status': 404,
		'message': 'Not Found: ' + request.url,
	}

	resp = jsonify(message)
	resp.status_code = 404
	
	return resp


app.error_handler_spec[None][404] = not_found


@app.route('/users/<userid>', methods = ['GET'])
def api_users(userid):
	users = {'1':'James','2':'Ashley'}
	
	if userid in users:
		return jsonify({userid:users[userid]})
	else:
	   return not_found()



def check_auth(username, password):
	return username == 'admin' and password == 'ashley'


def authenticate():
	message = {'message': "Authenticate"}
	resp = jsonify(message)
	
	resp.status_code = 401
	resp.headers['WWW-Authenticate'] = 'Basic realm="EXAMPLE"'
	
	return resp


def requires_auth(f):
	@wraps(f)
	def decorated(*args, **kwargs):
		auth = request.authorization
		if not auth:
			return authenticate()

		elif not check_auth(auth.username, auth.password):
			return authenticate()
	        return f(*args, **kwargs)

        return decorated
	

@app.route('/secrets')
@requires_auth
def api_auth_hello():
    return "Shhh james I am going !"



app.route('/messages', methods = ['PUT'])
def api_message():
	
	if request.headers['Content-Type'] == 'text/plain':
		return "Text Message: " + request.data
	
	elif request.headers['Content-Type'] == 'application/json':
		return "JSON Message: " + json.dumps(request.json)
	
	else:
	        return "415 Unspported Media Type :)"


@app.route('/hello')
def api_hello():
   if 'name' in request.args:
	return 'Hello ' + request.args['name']
   else:
        return 'Hello Ashley'

if __name__ == '__main__':
	app.run(host='0.0.0.0', debug=True)


