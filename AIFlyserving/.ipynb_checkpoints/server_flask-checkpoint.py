import json
import os
import traceback
from flask import Flask, Response, jsonify, render_template, request,redirect,url_for,session
from model_loader import ModelLoader
import requests
import AIFlyserving
import yaml
#from redis_test import RedisDict

ai_server_config = {}

if 'AI_CONFIG' in os.environ:
    if os.path.exists(os.environ['AI_CONFIG']):
        with open(os.environ['AI_CONFIG']) as f:
            ai_server_config = yaml.load(f)

ROTATION_FILE_PATH = ai_server_config["rotation_status_file"]
app = Flask(__name__)
app.logger_name = "AI.app"
models_loaded = {}
model_loader = ModelLoader(ai_server_config)
try:
    if 'MODELS_TO_LOAD' in os.environ:
        models_to_load=os.environ['MODELS_TO_LOAD']
        model_list=[]
        model_version_list_args=models_to_load
        model_version_list=model_version_list_args.split(',')
        for model_version in model_version_list:
            model_name=model_version.split(':')[0]
            version=model_version.split(':')[1]
            model_list.append([model_name,version])
        models_to_load =model_list# json.loads(os.environ['MODELS_TO_LOAD'])
        print(models_to_load)
        models_loaded = model_loader.get_models_from_list(models_to_load)

except requests.exceptions.HTTPError as e:
    app.logger.error("Meta Service has thrown %s, the error is %s and stack trace is %s"
                     %(e.response.status_code, e.message, str(traceback.format_exc())))
    raise RuntimeError("Meta Service has thrown '{}' , the error is {} and stack trace is {}".format(e.response.status_code, e.message, str(traceback.format_exc())))

app.logger.info("Loaded models are: " + json.dumps(models_loaded.keys()))
from abc import ABCMeta, abstractmethod

import json
import logging
from jinja2 import Template


def gen_python_api(json_data, model_name,model_version,endpoint="http://127.0.0.1:8400"):
    """
    Generate TensorFlow SDK in Python.
    Args:
    generated_tensor_data: Example is {"keys": [[1.0], [2.0]], "features": [[1, 1, 1, 1, 1, 1, 1, 1, 1], [1, 1, 1, 1, 1, 1, 1, 1, 1]]}
    """

    code_template = """#!/usr/bin/env python

    import requests

    def main():
        #endpoint = "http://127.0.0.1:8000"
        endpoint = {{endpoint}}
        param={"model_name": "{{ model_name }}", "model_version": "{{ model_version }}"}
        json_data = {{json_data}}
        result = requests.post(endpoint, param=param,json=json_data)
        print(result.text)

    if __name__ == "__main__":
        main()
    """

    generated_tensor_data_string = json.dumps(json_data)
    template = Template(code_template)
    generate_code = template.render(
        model_name=model_name, model_version=model_version,json_data=generated_tensor_data_string,endpoint=endpoint)
    logging.debug("Generate the code in Python:\n{}".format(generate_code))
    return generate_code





class NumpyEncoder(json.JSONEncoder):
    def default(self, obj):
        if isinstance(obj, np.ndarray):
            return obj.tolist()
        return json.JSONEncoder.default(self, obj)
import requests
def predict_client(model_server_url,params,data):
    model_server_url =model_server_url+'/predict'# "http://localhost:8000/predict"
    #params = {"model_id":"fib_model", "model_version":"1.0.2"}
    #data = json.dumps({"data":11})
    response = requests.post(model_server_url, params = params, json = data)
    return response.content#eval(response.content)['result']


app.secret_key='\xf1\x92Y\xdf\x8ejY\x04\x96\xb4V\x88\xfb\xfc\xb5\x18F\xa3\xee\xb9\xb9t\x01\xf0\x96' 
@app.route("/login",methods=['POST','GET'])
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
#test=RedisDict(namespace='web_ui')
class InferenceService(object):
    """
    The abstract class for inference service which should implement the method.
    """
    __metaclass__ = ABCMeta

    def __init__(self,model_name,model_version, model_graph_signature=None, platform=None):
        self.model_name = model_name
        self.model_base_path = None
        self.model_version = model_version
        self.model_graph_signature = model_graph_signature
        self.platform = platform
model_name_service_map={}
for m_list in models_to_load:
    model_name,model_version=m_list
    generated_tensor_data={"keys": [[1.0], [2.0]], "features": [[1, 1, 1, 1, 1, 1, 1, 1, 1], [1, 1, 1, 1, 1, 1, 1, 1, 1]]}
    graph_api_info=gen_python_api(generated_tensor_data,model_name,model_version=model_version)
    model_name_service_map[model_name]=InferenceService(model_name=model_name,
                                                        model_version=model_version,
                                                        model_graph_signature=graph_api_info,
                                                        platform=model_name.split('_')[0])
@app.route("/index", methods=["GET"])
def index():
    if session.get('username')=='admin' and session.get('password')=='admin123':
        """
        model_name_service_map_redis={}
        dict_redis=test['model_info']
        for kk in dict_redis['model_config_list']:
            model_name_service_map_redis[kk['name']]=InferenceService(kk['name'],kk['base_path'],kk['platform'])
        print(model_name_service_map_redis)        
        """

        return render_template("index.html", model_name_service_map=model_name_service_map)
    return "you are not logged in" 
@app.route('/json_inference', methods=["GET"])
def json_inference():
    return render_template('json_inference.html')

from gen_client import python_client

@app.route('/run_json_inference', methods=['POST'])
def run_json_inference():
    json_data_string = request.form["json_data"]
    json_data = json.loads(json_data_string)
    model_name = request.form["model_name"]
    model_name_re=model_name.split(':')[0]
    model_name_version=model_name.split(':')[1]
    param={"model_id":model_name_re,"model_version":model_name_version}
    request_json_data = {"model_name": model_name, "data": json_data}
    #predict_client
    

    predict_result = predict_client("http://0.0.0.0:8000",param, json.dumps(json_data))
    print(param,json_data,predict_result)  
    return render_template('json_inference.html', predict_result=predict_result)


@app.route('/elb-healthcheck', methods=['GET'])
def elb_healthcheck():
    try:
        if os.path.isfile(ROTATION_FILE_PATH):
            with open(ROTATION_FILE_PATH) as fd:
                lines = (fd.read()).strip()
                if lines == '1':
                    #TODO: uptime, requests and capacity have to be computed
                    result = {"uptime": 0, "requests": 0, "capacity": 100}
                    return jsonify(result)
        response = jsonify({'Message': "Out of rotation"})
        response.status_code = 500
        return response
    except Exception as e:
        response = jsonify({'Message': "Out of rotation"})
        response.status_code = 500
        return response

@app.route('/rotation_status', methods=['POST'])
def rotation_status():
    try:
        state = request.args.get('state')
        if state is not None:
            if state == "oor" or state == "OOR":
                write_rotation_status(ROTATION_FILE_PATH, '0')
                result = {'Message': "Taking out of rotation"}
                return jsonify(result)
            elif state == "bir" or state == "BIR":
                write_rotation_status(ROTATION_FILE_PATH, '1')
                result = {'Message': "Taking back in rotation"}
                return jsonify(result)
            else:
                response = jsonify({'Message': "Bad Request"})
                response.status_code = 400
                return response
        else:
            response = jsonify({'Message': "Bad Request"})
            response.status_code = 400
            return response
    except Exception as e:
        result = {'Message': str(e)}
        return jsonify(result)


@app.route('/models-loaded', methods=['GET'])
def models_available():
    response = jsonify({"result":models_loaded.keys()})
    response.status_code = 200
    return response

@app.route('/health', methods=['GET'])
def health():
    app.logger.debug("Health Check")
    try:
        if os.path.isfile(ROTATION_FILE_PATH):
            with open(ROTATION_FILE_PATH) as fd:
                lines = (fd.read()).strip()
                if lines == '1':
                    result = {"version": AIFlyserving.__version__, "health_status": "OK"}
                    return json.dumps(result)
        response = jsonify({'Message': "Out of rotation"})
        response.status_code = 500
        return response
    except Exception as e:
        exc_traceback = str(traceback.format_exc())
        app.logger.error("Exception occurred: " + str(e.message) + "," + exc_traceback)
        response = jsonify({"stack_trace": exc_traceback})
        response.status_code = 500
        return response
@app.route('/API_stat', methods=["GET"])
def API_stat():
    return render_template('API_stat.html')

@app.route('/image_inference', methods=["GET"])
def image_inference():
    return render_template('image_inference.html')



@app.route('/run_image_inference', methods=['POST'])
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

@app.route('/predict', methods=['POST'])
def predict():
    try:
        try:
            input = json.loads(request.data)
        except ValueError as e:
            stack_trace = traceback.format_exc()
            app.logger.error("Json Decoding failed. Check if the payload is correct. Payload is " +
                             str(request.data) + " and the stack_trace is " + stack_trace)
            response = jsonify({"result": "NA", "error": "Json Decoding failed. Check if the payload is correct",
                                "exception": str(e), "stack_trace": stack_trace})
            response.status_code = 400
            return response
        model_id = request.args.get('model_id')
        model_version = request.args.get('model_version')
        key = (model_id, model_version)

        try:
            curr_model = models_loaded[key]
        except KeyError:
            app.logger.error("Model: (%s,%s) doesn't exist " %(model_id, model_version))
            response = jsonify({"result":"NA", "stack_trace" : "Model: (%s,%s) doesn't exist. Deploy this model on AI server " %(model_id, model_version)})
            response.status_code = 400
            return response
        input2=eval(input)['data']
        print(input2,type(input2))
        output = curr_model.predict(input2)
        response = jsonify(json.loads(json.dumps(output,cls=NumpyEncoder)))
        #jsonify(json.loads(json.dumps({"result":output,"status":"success!"},cls=NumpyEncoder))))
        response.status_code = 200
        return response
    except Exception as e:
        exc_traceback = str(traceback.format_exc())
        app.logger.error("Exception occurred: " + str(e) + "," + exc_traceback)
        response = jsonify({"result":"NA", "stack_trace": exc_traceback})
        response.status_code = 500
        return response


def lock(lockfile):
    import fcntl
    lockfd = open(lockfile, 'w+')
    fcntl.flock(lockfd, fcntl.LOCK_EX | fcntl.LOCK_NB)
    return lockfd


def unlock(lockfd):
    import fcntl
    fcntl.flock(lockfd, fcntl.LOCK_UN)

def write_rotation_status(file_path, status):
    if os.path.isfile(file_path):
        with open(file_path) as f:
            lines = f.read().strip()
            if lines == status:
                return
    lockfile = file_path + '.lock'
    if not os.path.exists(lockfile):
        fd = open(lockfile, 'w+')
        fd.close()

    lockfd = lock(lockfile)
    file = open(file_path, 'w+')
    file.write(status)
    file.close()
    unlock(lockfd)
