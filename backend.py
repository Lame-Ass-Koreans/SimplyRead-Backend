import sys
import json
import re

from flask_cors import CORS
from flask import Flask, request, jsonify
from flask_restful import Resource, Api
from json import dumps


bad_words_txt = open('badwords.txt', 'r').read()
bad_words_arr = bad_words_txt.splitlines()
print(bad_words_arr)



class REMOVE_BAD_WORDS(Resource):
    def get(self, target_string):
        for bad_word in bad_words_arr:
           target_string = re.sub(bad_word, '****', target_string)
        return {
            "data" : target_string
        }



app = Flask(__name__)
api = Api(app)
CORS(app)

#api.add_resource(REMOVE_BAD_WORDS,'/badwords?<string:todo_id>')

@app.route('/success/<name>')
def success(name):
   return 'welcome %s' % name

@app.route('/badwords',methods = ['GET'])
def badwords():
    target_string = request.args.get('target_string')
    for bad_word in bad_words_arr:
        bad_word = bad_word.replace('*', '').replace("(", '')
        target_string = re.sub(r'\b{}\b'.format(bad_word), '****', target_string, flags=re.I)
    response = jsonify({"data" : target_string})
    response.headers.add('Access-Control-Allow-Origin', '*')
    return response

MYPORT = sys.argv[1]

if __name__ == '__main__':
     app.run(host = "0.0.0.0",port=int(MYPORT))
