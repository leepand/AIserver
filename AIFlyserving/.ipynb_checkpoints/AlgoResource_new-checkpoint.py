# -*- coding:utf-8 -*-
import falcon
import json
import sys
import logging
from AIFlysdk.AIFlyApi import AIFlyApi
from AIFlyserving.model_loader import ModelLoader
import yaml

try:
    from inspect import signature, _empty
except:
    from funcsigs import signature, _empty
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger('Algo Engine')
PY2 = (sys.version_info.major == 2)
PY3 = (sys.version_info.major == 3)

class PredictionInput:
    """
    Contains input details and model_id and data
    model_id:'tensormodel'
    model_version:'0.1.0
    data:
        - input:数据输入
    """  
    def __init__(self,model_id,model_version,data):
        self.model_id=model_id
        self.model_version=model_version
        self.data=data

class ModelInput:
    """
    Contains input details and model_id and data
    funcslist:['predpy.pred']
        - predpy:文件名
        - pred:函数名
    """  
    def __init__(self,funcslist):
        self.funcslist=funcslist
class AlgoResource(object):
    def __init__(self,config,model_list):
        self.logger = logging.getLogger(__name__)
        self.conf=config#'config/AIFlyapi_config.yaml'
        self.models_loaded={}
        with open(self.conf, 'rt') as f:
            self.client_config = yaml.load(f.read())
        #model_list=[['fib_model','1.0.2']]
        #model_loader = ModelLoader(self.client_config)
        #models_to_load=model_list
        model_loader = ModelLoader(self.client_config)
        self.model_list=model_list
        self.models_loaded =model_loader.get_models_from_list(self.model_list)#model_loader.get_models_from_list(models_to_load)

    def on_get(self, req, resp):
        """Handles GET requests"""
        
        resp.status = falcon.HTTP_200  # This is the default status
        resp.body = ('\nFalcon is awesome! \n')
    def on_put(self, req, resp):
        """Handles PUT requests for model init"""
        funcs_to_service_map = json.loads(req.stream.read())
        self.logger.debug('Update request received with payload: %s', str(funcs_to_service_map))
        model_list=funcs_to_service_map['model_list']
        model_loader = ModelLoader(self.client_config)
        models_to_load=model_list
        self.models_loaded = model_loader.get_models_from_list(models_to_load)
        #model_list=[["HelloWorldExample", "1.0.0"],["HelloAI2", "1.0.0"],["TensorflowMnistExample","1.0.0"],['fib_model',"1.0.2"]]
        
        resp.status = falcon.HTTP_200
        #resp.content=json.dumps({"reg info":"sucess"})
        resp.body = json.dumps({"Init Model Service": "Success"})
    def on_post(self, req, resp):
        payload = json.loads(req.stream.read())

        if ('data' in payload.keys()) and ('modelId' in payload.keys()):
            PredictionInput.data = payload['data']
            PredictionInput.model_id = payload['modelId']
            PredictionInput.model_version=payload['model_version']
            key = (PredictionInput.model_id, PredictionInput.model_version)
            curr_model = self.models_loaded[key]
             
        else:
            resp.status = falcon.HTTP_400
            raise falcon.HTTPBadRequest("Bad Request", "Url and(or) modelId missing in the payload")

        #result=algo_engine.call_func(fun_path,**{'n':42})
        try:
            po = json.dumps({'result':curr_model.predict(PredictionInput.data)})
            resp.status = falcon.HTTP_200
            resp.body = po
        except:
            resp.body = json.dumps({'status': 'Failure', 'message' : 'Error occurred'})
            resp.status = falcon.HTTP_500
            raise falcon.HTTPInternalServerError('Internal Server Error', 'Predict failed! ')
        '''
        if po.bo.status == 'Success':
            resp.status = falcon.HTTP_200
            resp.body = (str(po.values))
        elif po.bo.status == 'Failure':
            resp.body = json.dumps({'status': 'Failure', 'message' : 'Error occurred'})
            resp.status = falcon.HTTP_500
            raise falcon.HTTPInternalServerError('Internal Server Error', 'Predict failed! ')       
        '''