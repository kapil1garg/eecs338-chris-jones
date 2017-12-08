#!flask/bin/python
from urlparse import urlparse
from chrisjones import ChrisJones

from flask import Flask
from flask import jsonify
from flask import request
from flask_api import status

app = Flask(__name__)
controller = ChrisJones()


@app.route('/')
def index():
    return "Hello, World!"

# TODO: handle any errors coming from chrisjones.py and send a bad status code
@app.route('/chrisjones/api/v1.0/respond', methods=['POST'])
def respond_to_query():
    return jsonify({'response': controller.respond(request.form['query'])}), status.HTTP_200_OK


if __name__ == '__main__':
    app.run(debug=True)
