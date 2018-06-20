
from __future__ import absolute_import
from __future__ import division
from __future__ import print_function

import argparse
#import argcomplete
import os
import io
import json
import logging
import sys
from functools import wraps
import numpy as np
from flask import Flask, Response, jsonify, render_template, request,redirect,url_for,session
from PIL import Image
from flask_cors import CORS


logging.basicConfig(level=logging.DEBUG)

# Define parameters
parser = argparse.ArgumentParser()

# TODO: Remove if it does not need gunicorn
parser.add_argument(
    "--bind",
    default="0.0.0.0:8500",
    help="Bind address of the server(eg. 0.0.0.0:8500)")
parser.add_argument(
    "--host", default="0.0.0.0", help="The host of the server(eg. 0.0.0.0)")
parser.add_argument(
    "--port", default=8500, help="The port of the server(eg. 8500)", type=int)
parser.add_argument(
    "--model_name",
    default="default",
    help="The name of the model(eg. default)")
parser.add_argument(
    "--model_base_path",
    default="./model",
    help="The file path of the model(eg. 8500)")
parser.add_argument(
    "--model_platform",
    default="tensorflow",
    help="The platform of model(eg. tensorflow)")
parser.add_argument(
    "--model_config_file",
    default="",
    help="The file of the model config(eg. '')")
# TODO: type=bool not works, make it true by default if fixing exit bug
parser.add_argument(
    "--reload_models", default="False", help="Reload models or not(eg. True)")
parser.add_argument(
    "--custom_op_paths",
    default="",
    help="The path of custom op so files(eg. ./)")
parser.add_argument(
    "--verbose",
    default=True,
    help="Enable verbose log or not(eg. True)",
    type=bool)
parser.add_argument(
    "--gen_client", default="", help="Generate the client code(eg. python)")
parser.add_argument(
    "--enable_auth",
    default=False,
    help="Enable basic auth or not(eg. False)",
    type=bool)
parser.add_argument(
    "--auth_username",
    default="admin",
    help="The username of basic auth(eg. admin)")
parser.add_argument(
    "--auth_password",
    default="admin",
    help="The password of basic auth(eg. admin)")
parser.add_argument(
    "--enable_colored_log",
    default=False,
    help="Enable colored log(eg. False)",
    type=bool)
parser.add_argument(
        "--enable_cors",
        default=True,
        help="Enable cors(eg. True)",
        type=bool)

# TODO: Support auto-complete
#argcomplete.autocomplete(parser)

if len(sys.argv) == 1:
    args = parser.parse_args(["-h"])
    args.func(args)
else:
    args = parser.parse_args(sys.argv[1:])
    for arg in vars(args):
        logging.info("{}: {}".format(arg, getattr(args, arg)))

    if args.enable_colored_log:
        import coloredlogs
        coloredlogs.install()

# TODO: Support auto-complete
#argcomplete.autocomplete(parser)


from abc import ABCMeta, abstractmethod


class InferenceService(object):
    """
    The abstract class for inference service which should implement the method.
    """
    __metaclass__ = ABCMeta

    def __init__(self,model_name, model_base_path, platform=None):
        self.model_name = model_name
        self.model_base_path = model_base_path
        self.model_version_list = [1]
        self.model_graph_signature = None
        self.platform = platform


class NumpyEncoder(json.JSONEncoder):
    def default(self, obj):
        if isinstance(obj, np.ndarray):
            return obj.tolist()
        return json.JSONEncoder.default(self, obj)


def verify_authentication(username, password):
  """
  Verify if this user should be authenticated or not.

  Args:
    username: The user name.
    password: The password.

  Return:
    True if it passes and False if it does not pass.
  """
  if args.enable_auth:
    if username == args.auth_username and password == args.auth_password:
      return True
    else:
      return False
  else:
    return True


def requires_auth(f):
    """
      The decorator to enable basic auth.
    """

    @wraps(f)
    def decorated(*decorator_args, **decorator_kwargs):
        auth = request.authorization

        if args.enable_auth:
            if not auth or not verify_authentication(auth.username, auth.password):
                response = Response("Need basic auth to request the resources", 401, {
                    "WWW-Authenticate": '"Basic realm="Login Required"'
                })
                return response

        return f(*decorator_args, **decorator_kwargs)

    return decorated
def login_required(func):
    @wraps(func)
    def wrapper(*args,**kwargs):
        if session.get('user_id'):
            return func(*args,**kwargs)
        else:
            return redirect(url_for('login'))
    return wrapper

# TODO: Check args for model_platform and others

# Initialize flask application
application = Flask(__name__, template_folder='templates')



UPLOAD_FOLDER = os.path.basename('static')
application.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER

application.secret_key='\xf1\x92Y\xdf\x8ejY\x04\x96\xb4V\x88\xfb\xfc\xb5\x18F\xa3\xee\xb9\xb9t\x01\xf0\x96' #login
model_name_service_map={}
x={
  "model_config_list": [
    {
      "name": "tensorflow_template_application_model",
      "base_path": "./models/tensorflow_template_application_model/",
      "platform": "tensorflow"
    }, {
      "name": "deep_image_model",
      "base_path": "./models/deep_image_model/",
      "platform": "tensorflow"
    }, {
       "name": "mxnet_mlp_model",
       "base_path": "./models/mxnet_mlp/mx_mlp",
       "platform": "mxnet"
    },
      {
       "name": "mxnet_mlp_model2",
       "base_path": "./models/mxnet_mlp/mx_mlp",
       "platform": "mxnet"
    },
      {
       "name": "mxnet_mlp_model3",
       "base_path": "./models/mxnet_mlp/mx_mlp",
       "platform": "mxnet"
    },
      {
       "name": "mxnet_mlp_model4",
       "base_path": "./models/mxnet_mlp/mx_mlp",
       "platform": "mxnet"
    },
      {
       "name": "mxnet_mlp_model5",
       "base_path": "./models/mxnet_mlp/mx_mlp",
       "platform": "mxnet"
    },
      {
       "name": "mxnet_mlp_model6",
       "base_path": "./models/mxnet_mlp/mx_mlp",
       "platform": "mxnet"
    }
  ]
}#{"name": "tensorflow_template_application", "base_path": "/", "platform": "tensorflow"}
# The API to render the dashboard page
for kk in x['model_config_list']:
    #InferenceService
    #print kk['name'],kk['base_path'],kk['platform']
    model_name_service_map[kk['name']]=InferenceService(kk['name'],kk['base_path'],kk['platform'])
    

@application.route("/login",methods=['POST','GET'])
def login():
    error = None
    if request.method == 'POST':
        session['username']=request.form['username']
        session['password']=request.form['password']
        if request.form['username'] != 'admin' or request.form['password'] != 'admin123': 
                error= "sorry"
        else:
            return redirect(url_for('index'))
    return render_template('login.html',error=error)
@application.route("/index", methods=["GET"])
def index():
    if session.get('username')=='admin' and session.get('password')=='admin123':
        return render_template("index.html", model_name_service_map=model_name_service_map)
    return "you are not logged in" 


# The API to rocess inference request
@application.route("/", methods=["POST"])
@login_required
def inference():
  # Process requests with json data
  if request.content_type.startswith("application/json"):
    json_data = json.loads(request.data)

  # Process requests with raw image
  elif request.content_type.startswith("multipart/form-data"):
    json_data = {}

    if "model_version" in request.form:
      json_data["model_version"] = int(request.form["model_version"])
    if "run_profile" in request.form:
      json_data["run_profile"] = request.form["run_profile"]

    image_cont1ent = request.files["image"].read()
    image_string = np.fromstring(image_content, np.uint8)
    if sys.version_info[0] < 3:
      import cStringIO
      image_string_io = cStringIO.StringIO(image_string)
    else:
      image_string_io = io.BytesIO(image_string)

    image_file = Image.open(image_string_io)
    if "channel_layout" in request.form:
      channel_layout = request.form["channel_layout"]
      if channel_layout in ["RGB", "RGBA"]:
        image_file = image_file.convert(channel_layout)
      else:
        logging.error("Illegal image_layout: {}".format(channel_layout))

    image_array = np.array(image_file)

    # TODO: Support multiple images without reshaping
    if "shape" in request.form:
      # Example: "32,32,1,3" -> (32, 32, 1, 3)
      shape = tuple([int(item) for item in request.form["shape"].split(",")])
      image_array = image_array.reshape(shape)
    else:
      image_array = image_array.reshape(1, *image_array.shape)

    json_data["data"] = {"image": image_array}
    #json_data["data"] = {"image_data": image_array}

  else:
    logging.error("Unsupported content type: {}".format(request.content_type))
    return "Error, unsupported content type"

  # Request backend service with json data
  #logging.debug("Constructed request data as json: {}".format(json_data))

  if "model_name" in json_data:
    model_name = json_data.get("model_name", "")
    if model_name == "":
      logging.error("The model does not exist: {}".format(model_name))
  else:
    model_name = "default"

  inferenceService = model_name_service_map[model_name]
  result = inferenceService.inference(json_data)

  # TODO: Change the decoder for numpy data
  return jsonify(json.loads(json.dumps(result, cls=NumpyEncoder)))


@application.route('/image_inference', methods=["GET"])
def image_inference():
    return render_template('image_inference.html')
@application.route('/API_stat', methods=["GET"])
def API_stat():
    return render_template('API_stat.html')


@application.route('/run_image_inference', methods=['POST'])
def run_image_inference():
  file = request.files['image']
  file_path = os.path.join(application.config['UPLOAD_FOLDER'], file.filename)
  file.save(file_path)

  channel_layout = "RGB"
  if "channel_layout" in request.form:
    channel_layout_ = request.form["channel_layout"]
    if channel_layout_ in ["RGB", "RGBA"]:
        channel_layout = channel_layout_

  run_profile = ""
  if "run_profile" in request.form:
    run_profile = request.form["run_profile"]

  image_file_path = os.path.join(application.config['UPLOAD_FOLDER'],
                                 file.filename)
  predict_result = python_predict_client.predict_image(
    image_file_path, channel_layout=channel_layout, run_profile=run_profile, port=args.port)

  return render_template(
      'image_inference.html',
      image_file_path=image_file_path,
      predict_result=predict_result)


@application.route('/json_inference', methods=["GET"])
def json_inference():
  return render_template('json_inference.html')


@application.route('/run_json_inference', methods=['POST'])
def run_json_inference():
  json_data_string = request.form["json_data"]
  json_data = json.loads(json_data_string)
  model_name = request.form["model_name"]

  request_json_data = {"model_name": model_name, "data": json_data}

  predict_result = python_predict_client.predict_json(request_json_data, port=args.port)

  return render_template('json_inference.html', predict_result=predict_result)


def main():
  # Start the HTTP server
  # Support multi-thread for json inference and image inference in same process
  application.run(host='127.0.0.1', port=8024, threaded=True)


if __name__ == "__main__":
  main()