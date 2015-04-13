#!/usr/bin/env python
# Ashley A
# Rest API for Elasticsearch allowing for certain methods and index operations


from flask import Flask, url_for, request, json, jsonify, Response
from functools import wraps
from datetime import datetime
from werkzeug.routing import BaseConverter
#from elasticsearch import Elasticsearch
es_url = "http://es.int.test.com.au:9200"

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


def FactoryMessage(msg):
	data = { 'Message': msg }
        resp = jsonify(data)
        resp.status_code = 200
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
        	                return FactoryMessage("Mappings not allowed!!!!!!")
			else:
				return FactoryMessage("Index not allowed!!!!!!")
	
	if request.method == 'GET':
                        app.logger.info(path[0])

                        if path[0] == 'builds':
                                ESURL = es_url + request.path[3:]
                                app.logger.info(ESURL)
                                r = requests.get(ESURL)
                                app.logger.info(r.content)
                                return r.content
			else:
                                return FactoryMessage("Index not allowed!!!!!!")
		

		
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


if __name__ == '__main__':
	app.run(host='0.0.0.0', debug=True)

