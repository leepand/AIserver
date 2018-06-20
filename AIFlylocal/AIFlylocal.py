# -*- coding:utf-8 -*-
from model_loader import ModelLoader
import json
import sys
import logging
from AIFlysdk.AIFlyApi import AIFlyApi
from model_loader import ModelLoader
import yaml

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
class PredictServer(object):
    def __init__(self,config):
        self.logger = logging.getLogger(__name__)
        self.conf=config#'config/AIFlyapi_config.yaml'
        self.models_loaded={}
        with open(self.conf, 'rt') as f:
            self.client_config = yaml.load(f.read())
        self.models_loaded = {}#model_loader.get_models_from_list(models_to_load)

    def load_models(self, model_list):
        """Handles deployed model for init"""
        self.logger.debug('Update models received with payload: %s', str(model_list))
        model_loader = ModelLoader(self.client_config)
        models_to_load=model_list
        self.models_loaded = model_loader.get_models_from_list(models_to_load)
        #model_list=[["HelloWorldExample", "1.0.0"],["HelloAI2", "1.0.0"],["TensorflowMnistExample","1.0.0"],['fib_model',"1.0.2"]]
        
        return json.dumps({"Init Model Service": "Success"})
    def predict(self, *args,**kwargs):
        #PredictionInput.data = *args
        if ('model_version' in kwargs.keys()) and ('modelId' in kwargs.keys()):   
            PredictionInput.model_id = kwargs['modelId']
            PredictionInput.model_version=kwargs['model_version']
            key = (PredictionInput.model_id, PredictionInput.model_version)
            curr_model = self.models_loaded[key]
             
        else:           
            print("Bad Request", "model_version and(or) modelId missing in the payload")
        try:
            po = json.dumps({'result':curr_model.predict(*args)})
            return po
        except:
            return json.dumps({'status': 'Failure', 'message' : 'Error occurred'})