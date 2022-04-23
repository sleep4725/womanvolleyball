from flask import Flask, render_template 
import os
import sys
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from es.ElasticClient import ElasticClient

esClient = ElasticClient.ret_es_client() 

app = Flask(__name__)
app.config['JSON_AS_ASCII'] = False

@app.route("/", methods=['GET'])
def index():
    return "hello world"

@app.route("/player/<name>", methods=['GET'])
def player(name: str):
    dslQuery = {
        "query": {
            "term": {
                "name": {
                    "value": name
                }
            }
        }
    } 
    
    response = esClient.search(index="women_volleyball", body=dslQuery)
    
    return render_template("player-information.html", data=response)

if __name__ == "__main__":
    app.run(host="0.0.0.0",
            port=9999,
            debug=True)
