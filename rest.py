
# def timestamp():
#   return int(time.time())

import os
from flask import Flask, Response, request, abort, jsonify, flash, redirect, url_for
from werkzeug.contrib.fixers import ProxyFix

from werkzeug.utils import secure_filename

import generator
from zones import zones

UPLOAD_FOLDER = '/path/to/the/uploads'
ALLOWED_EXTENSIONS = set(['txt', 'pdf', 'png', 'jpg', 'jpeg', 'gif'])

app = Flask(__name__)
app.config['SESSION_TYPE'] = 'filesystem'
app.config['SECRET_KEY'] = app.secret_key = os.urandom(470)



app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER
app = Flask(__name__)
app.wsgi_app = ProxyFix(app.wsgi_app)

@app.route('/', methods=['POST'])
def template_uploaded():
  if request.method == 'POST':
    file = request.files['file']
    filename = secure_filename(file.filename)
    template = file.stream.read().decode()
    template = generator.subnet().expand(zones=zones, template=template)
    template = generator.rublacklist().expand_from_cache(template)
    return template

if __name__ == '__main__':
  app.run(host='0.0.0.0',port=8080,debug=True)

