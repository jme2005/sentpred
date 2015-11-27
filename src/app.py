# -*- coding: utf-8 -*-
"""
Created on Fri Nov 27 15:39:38 2015

@author: edvinj
"""

import random
import string
import cherrypy
import sent_pred
import json
import sys


model_dir = "../models/"


class AutosuggestGenerator(object):
     
    @cherrypy.expose
    def index(self):
        return "Hello world!"

    @cherrypy.expose
    def autosuggest(self,q=""):
        data = {}
        data['Suggestions'] = model.predict(q)
        return json.dumps(data)
        
if __name__ == '__main__':
    
    if len(sys.argv) > 1:
        modelname = sys.argv[1]
    else:
        modelname = "small.json"
    model = sent_pred.SentencePredictor()
    model.load(model_dir+modelname)
    cherrypy.quickstart(AutosuggestGenerator())