# -*- coding:utf-8 -*-
import falcon
import os
import sys
import time
import argparse
import logging
#sys.path.append(os.path.join(os.path.dirname(__file__), "../../../"))
import json
import yaml
import traceback

from AlgoResource_new import AlgoResource

#from commons.src.elb.elb_resource import ElbResource
parser = argparse.ArgumentParser()
logging.basicConfig(level=logging.DEBUG)
# TODO: Remove if it does not need gunicorn
import ast
parser.add_argument(
    "--model_list",
    default="default",
    help="The list of the model to be deployed(eg. default)")
parser.add_argument(
    "--model_config_file",
    default="config/AIFlyapi_config.yaml",
    help="The file of the model config(eg. '')")
# TODO: type=bool not works, make it true by default if fixing exit bug

parser.add_argument(
    "--gen_client", default="", help="Generate the client code(eg. python)")
if len(sys.argv) == 1:
    args = parser.parse_args(["-h"])
    args.func(args)
else:
    args = parser.parse_args(sys.argv[1:])
    for arg in vars(args):
        logging.info("{}: {}".format(arg, getattr(args, arg)))



hunch_server_config = {}

if 'AI_CONFIG' in os.environ:
    if os.path.exists(os.environ['AI_CONFIG']):
        conf_file=os.environ['AI_CONFIG']
        with open(os.environ['AI_CONFIG']) as f:
            ai_server_config = yaml.load(f)


try:
    if 'MODELS_TO_LOAD' in os.environ:
        models_to_load = os.environ['MODELS_TO_LOAD']#json.loads(os.environ['MODELS_TO_LOAD'])
        #models_loaded = model_loader.get_models_from_list(models_to_load)

except:
    pass

model_list=[]
model_version_list_args=models_to_load
model_version_list=model_version_list_args.split(',')
for model_version in model_version_list:
    model_name=model_version.split(':')[0]
    version=model_version.split(':')[1]
    model_list.append([model_name,version])
def loader():

    start_time = int(time.time())

    print(model_list)
    algoResource = AlgoResource(conf_file,model_list)
    # falcon.API instances are callable WSGI apps
    app = falcon.API()
    # caffe_model will handle all requests to the '/caffe_model' URL path
    app.add_route('/AI_server/predict/', algoResource)
    #app.add_route('/elb-healthcheck', elb_resource)
app=loader()

def main():
    # Start the HTTP server
    # Support multi-thread for json inference and image inference in same process
   	
    #return app
    #server = make_server('0.0.0.0', 8009, app)
	#server.serve_forever()
    httpd = simple_server.make_server('127.0.0.1', 8000, app)
    httpd.serve_forever()
