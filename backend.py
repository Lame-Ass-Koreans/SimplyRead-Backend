import sys
import json
import re

from flask_cors import CORS
from flask import Flask, request, jsonify, abort
from flask_restful import Resource, Api
from json import dumps
import couchdb

from nltk.corpus import wordnet

bad_words_txt = open('badwords.txt', 'r').read()
bad_words_arr = bad_words_txt.splitlines() 

common_words_text = open('google-10000-english.txt', 'r').read()
common_words_arr = common_words_text.splitlines()

couch = couchdb.Server('http://admin:password@127.0.0.1:5984/')
print('reach')
for dbname in couch:
    print(dbname)
db = couch['simpleready']

app = Flask(__name__)
api = Api(app)
CORS(app)

#api.add_resource(REMOVE_BAD_WORDS,'/badwords?<string:todo_id>')

@app.route('/success/<name>')
def success(name):
   return 'welcome %s' % name

@app.route('/login', methods=['GET'])
def login():
    username = request.args.get('username')
    password = request.args.get('password')
    docs = list(db.find({'selector': {'username': username, 'password': password}}))
    print(docs)
    if len(docs) == 0:
        abort(404)
    else:
        return docs[0]

@app.route('/badwords',methods = ['GET'])
def badwords():
    target_string = request.args.get('target_string')
    for bad_word in bad_words_arr:
        bad_word = bad_word.replace('*', '').replace("(", '')
        target_string = re.sub(r'\b{}\b'.format(bad_word), '****', target_string, flags=re.I)
    response = jsonify({"data" : target_string})
    response.headers.add('Access-Control-Allow-Origin', '*')
    return response

@app.route('/simplify', methods = ['GET'])
def simplify():
    rVal = ""
    target_string = request.args.get('target_string')
    replacement_dictionary={}
    target_string_lines = target_string.splitlines()
    for target_line in target_string_lines:
        target_string_words = target_line.split()
        for target_word in target_string_words:
            if target_word.lower() not in common_words_arr:
                if target_word.lower() not in replacement_dictionary:
                    syn = synonym(target_word.lower())
                    if not syn == target_word.lower():
                        replacement_dictionary[target_word.lower()] = syn
                        rVal += replacement_dictionary[target_word.lower()] + " "
                    else:
                        rVal += target_word.lower() + " "
                else:
                    rVal += replacement_dictionary[target_word.lower()] + " "

            else:
                rVal += target_word + " "
        rVal += "\n"
    response = jsonify({"data" : rVal, "dict" : replacement_dictionary})
    return response

def synonym(target):
    synList = wordnet.synsets(target)
    if (len(synList) > 1):
        return synList[0].name()[0:synList[0].name().find('.')]
    else:
        return target

MYPORT = sys.argv[1]

if __name__ == '__main__':
     app.run(host = "0.0.0.0",port=int(MYPORT))
