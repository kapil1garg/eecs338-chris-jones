#!flask/bin/python
from urlparse import urlparse
from chrisjones import ChrisJones
from flask import Flask
from flask import jsonify
from flask import request

app = Flask(__name__)
controller = ChrisJones()

@app.route('/')
def index():
    return "Hello, World!"

@app.route('/chrisjones/api/v1.0/respond', methods=['POST'])
def respond_to_query():
    return jsonify({'response': controller.respond(request.form['query'])})

if __name__ == '__main__':
    app.run(debug=True)