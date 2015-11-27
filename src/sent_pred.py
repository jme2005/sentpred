# -*- coding: utf-8 -*-
"""
Created on Wed Nov 25 21:18:05 2015

@author: edvinj
"""

import nltk
from collections import defaultdict
import json
import pickle
import time

class SentencePredictor:
    
    def __init__(self, 
                 p=0.02,
                 fuzzy=True,
                 startfuzzy=2):
        
        self.p = p
        self.model = {}
        self.fuzzy = True
        self.startfuzzy = startfuzzy
        self.model['edit1'] = None
        self.model['edit2'] = None
        self.model['lookup'] = None
        
        
    def train(self,path,threshold=1,e1=True,e2=False):
        sents = self._extracttext(path,threshold)
        self.model['lookup'] =self._build_lookup(sents)
        if e2:
            self._get_edit2()
        elif e1:
            self._get_edit1()
        
    def predict(self,inputstring):
        if not self.model['lookup']:
            print "No model is loaded"
            return
            
        e1, e2 = None, None
        inputstring = inputstring.lower()
        if self.model['edit1'] and\
                (len(inputstring) > self.startfuzzy) and self.fuzzy:
            try:
                e1 = set(self.model['edit1'][inputstring])
            except:
                pass
        if self.model['edit2'] and\
                (len(inputstring) > self.startfuzzy) and self.fuzzy:
            try:
                e2 = set(self.model['edit2'][inputstring])
            except:
                pass
            
        if not self.model['edit1'] and\
                self.fuzzy and\
                len(inputstring) > self.startfuzzy:
            e1 = self._edits1(inputstring)
            
        try:    
            hits = [item for item in self.model['lookup'][inputstring][-5:]]
            minimum = self._getvalue(hits[0])
        except:
            hits = []
            minimum = 0
            
        if e1:
            for item in e1:
                try:
                    hits_tmp = self.model['lookup'][item][-5:]
                except:
                    continue
                for hit in hits_tmp:
                    prob = float(hit[1]) * (1-(1-self.p)**len(item))
                    if prob > minimum:
                        hits.append((hit[0], prob))
            if e2:
                for item in e2:
                    try:
                        hits_tmp = self.model['lookup'][item].items()
                    except:
                        continue
                    for hit in hits_tmp:
                        hits.append((hit[0], int(hit[1]) * (1-(1-self.p**2)**len(item))))
            
        hits = set(hits)    
        output = sorted(hits,key=self._getvalue)[-5:]
        return [item[0] for item in output]
    
    def save(self,path):
        with open(path,'wb') as fp:
            json.dump(self.model,fp)
    
    def load(self,path):
        with open(path, 'rb') as fp:
            self.model = json.load(fp)
            
    def timepredictions(self,inputstring,n):
        tic = time.time()
        for i in range(n):
            self.predict(inputstring)
        tac = time.time()
        print tac - tic
        
    def evaluate(self,sentences):
        score = 0
        for sent in sentences:
            for n in range(len(sent)/2):
                res = set(self.predict(sent[:n]))
                if sent in res:
                    score += 1
                    break
                     
        fraction = str(round(float(score)/len(sentences),2))
        print "The model accurately predicted %s of the sentences" % (fraction)
            

    def _get_edit1(self):
        keys = self.model['lookup'].keys()
        edit1 = defaultdict(list)
        for n,key in enumerate(keys):
            for e1 in self._edits1(key):
                edit1[e1].append(key)
        self.model['edit1'] = edit1
    
    def _get_edit2(self):
        keys = self.model['lookup'].keys()
        edit1 = defaultdict(list)
        edit2 = defaultdict(list)
        for n,key in enumerate(keys):
            for e1 in self._edits1(key):
                edit1[e1].append(key)
                for e2 in self._edits1(e1):
                    edit2[e2].append(key)
        self.model['edit1'] = edit1
        self.model['edit2'] = edit2
        
    def _edits1(self,word):
        alphabet = 'abcdefghijklmnopqrstuvwxyz'
        word = word.lower()
        splits     = [(word[:i], word[i:]) for i in range(len(word))]
        deletes    = [a + b[1:] for a, b in splits if b]
        transposes = [a + b[1] + b[0] + b[2:] for a, b in splits if len(b)>1]
        replaces   = [a + c + b[1:] for a, b in splits for c in alphabet if b]
        inserts    = [a + c + b     for a, b in splits for c in alphabet]
        return set(deletes + transposes + replaces + inserts) - set([word,word[:-1]])
        
    def _build_lookup(self,sents):
        lookup_dict = defaultdict(lambda: defaultdict(lambda: 0))
        for sentence in sents:
            for n in range(len(sentence)):
                lookup_dict[sentence[:n].lower()][sentence] += 1
        self._sortdict(lookup_dict)
        return lookup_dict
    
    def _extracttext(self,path,threshold):
        with open(path,'rb') as fp:
            indict = json.load(fp,encoding="UTF-8")
        sents = []
        for item in  indict['Issues']:  
            for message in item['Messages']:
                if message['IsFromCustomer']:      
                    continue
                else:
                    sents.append(message['Text'])
                    
        sents = [nltk.sent_tokenize(item) for item in sents]
        sents = [item.strip() for sublist in sents for item in sublist]
        sents = self._clearthreshold(sents,threshold)
    
        return sents 
    
    def _clearthreshold(self,sents,threshold):
        tmpdict = defaultdict(lambda: 0)
        for sent in sents:
            tmpdict[sent] +=1
        output = []
        for key, value in tmpdict.items():
            if value > threshold:
                for i in range(value):
                    output.append(key)             
        return output
    
        
    def _getvalue(self,tup1):
        return tup1[1]
        
    def _sortdict(self,dictionary):
        for subdict in dictionary.keys():
            dictionary[subdict] = sorted(dictionary[subdict].items(),
                                                   key=self._getvalue)
        
    
        


    
    
        
    