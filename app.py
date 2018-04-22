#!/usr/bin/env python3

# def timestamp():
#   return int(time.time())

import os

import markdown2
from flask import Flask, Response, request, abort, jsonify, flash, redirect, url_for
from werkzeug.contrib.fixers import ProxyFix
from werkzeug.utils import secure_filename

import generator as provider
from zones import zones

UPLOAD_FOLDER = '/path/to/the/uploads'
ALLOWED_EXTENSIONS = set(['txt', 'pdf', 'png', 'jpg', 'jpeg', 'gif'])

app = Flask(__name__)
app.config['SESSION_TYPE'] = 'filesystem'
app.config['SECRET_KEY'] = app.secret_key = 'The super secret for session handle. Modifyed from urandom 4 OpenShift run.'
# os.urandom(470)


app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER
app = Flask(__name__)
app.wsgi_app = ProxyFix(app.wsgi_app)

@app.route('/', methods=['POST'])
def template_uploaded():
  [ print(i) for i in request.files ]
  file = request.files['file']
  filename = secure_filename(file.filename)
  template = file.stream.read().decode()
  template = provider.subnets().expand(zones=zones, template=template)
  template = provider.rublacklist().expand_from_cache(template)
  return template

@app.route('/generator/', methods=['GET'])
def generator():
  return 'Done with exit code: {}'.format(
    os.system(
      'python3 generator.py'
    )
  )

@app.route('/', methods=['GET'])
def readme():
  with open('README.md') as f:
    return '<html><head><title>RKN vpn configurator</title></head><body>{}</body></html>'.format(
      markdown2.markdown(
        f.read()
      )
    )


if __name__ == '__main__':
  app.run(host='0.0.0.0',port=os.environ['PORT'],debug=True)

