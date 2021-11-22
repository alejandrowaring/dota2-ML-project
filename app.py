import os
from flask import (
    Flask,
    render_template,
    jsonify,
    request,
    redirect)
import pymongo
import json
from bson.json_util import ObjectId

# Setup Flask
app = Flask(__name__)
# #create connection variable
conn = 'mongodb://localhost:27017'
client = pymongo.MongoClient(conn)
db = client.dota_db
db.heroes.drop()

hero_json_file = os.path.join(".","data","heroes.json")
with open(hero_json_file) as json_file:
    data = json.load(json_file)
    for i in range(len(data)):
        currDict = data[i]
        currDict["img"] = "./static/images/heroes/" + str(currDict["id"]) + ".png"
        db.heroes.insert_one(currDict)


class MyEncoder(json.JSONEncoder):

    def default(self, obj):
        if isinstance(obj, ObjectId):
            return str(obj)
        return super(MyEncoder, self).default(obj)


app.json_encoder = MyEncoder

@app.route("/")
def home():
    return render_template("index.html")

@app.route("/predict",methods=['POST'])
def predict():
    heroes_id = [idize(x) for x in request.form.values()]
    #Create a matrix of heros to compare based on the input from the webapp
    enemy_heros = []

def idize(hero_name):
    current_search = db.heroes.find({"localized_name":hero_name})
    return current_search['id']