import os
from flask import (
    Flask,
    render_template,
    jsonify,
    request,
    redirect)
import json
#from bson.json_util import ObjectId
import joblib
import random
import numpy as np
from sklearn.preprocessing import OneHotEncoder
hero_json_file = os.path.join(".","data","heroes.json")

def remove_set(a,b):
    return list(set(a)-set(b))

def heroize(hero_id_list):
    output_hero_list = []
    with open(hero_json_file) as heroes_file:
        data = json.load(heroes_file)
        for i in hero_id_list:
            output_hero_list.append(next((item for item in data if item["id"] == i), None)['localized_name'])
    return output_hero_list

def idize(hero_name_list):
    output_hero_list = []
    with open(hero_json_file) as heroes_file:
        data = json.load(heroes_file)
        for i in hero_name_list:
            output_hero_list.append(next((item for item in data if item["localized_name"] == i), None)['id'])
    return output_hero_list

# Setup Flask
app = Flask(__name__)
num_heroes = 3

hero_ids = []
with open(hero_json_file) as heroes_file:
    data = json.load(heroes_file)
    #get all the possible hero ID's into a list
    for i in range(len(data)):
        currDict = data[i]
        hero_ids.append(currDict['id'])
matchups_all = []
#Create all possible matchups for the encoding
for i in hero_ids:
    for j in hero_ids:
        if i != j:
            matchups_all.append(str(i) + "-" + str(j))

            
        
# def idize(hero_name):
#     return current_search['id']

#Encoder for json file
# class MyEncoder(json.JSONEncoder):

#     def default(self, obj):
#         if isinstance(obj, ObjectId):
#             return str(obj)
#         return super(MyEncoder, self).default(obj)
# app.json_encoder = MyEncoder

@app.route("/")
def home():
    return render_template("index.html")

@app.route("/predict",methods=['POST'])
def predict():
    #Data Pulled from the forms
    our_heroes = [1,10,12]
    their_heroes = [13,16,20]
    hero_type = "Carry"
    #Load in the model and fit the Encoder
    model = joblib.load('./dota_picks_trained.h5')
    results = {}
    ohe = OneHotEncoder()
    X_all = np.array(matchups_all).reshape(-1,1)
    ohe.fit(X_all)
    #Open the json file ready to read so we can get the roles on the fly
    with open(hero_json_file) as heroes_file:
        heroes_json = json.load(heroes_file)
        #Remove the set of heroes that we already know are picked from the list of possible picks
        check_heroes = remove_set(hero_ids,our_heroes + their_heroes)
        #For each possible hero left to pick
        for i in check_heroes:
            sum = 0
            #If their Role matches the request
            if hero_type in next(item for item in heroes_json if item["id"] == i)['roles']:
                #Check the hero against however many heroes are passed in by the form
                for j in their_heroes:
                    #Just to be sure we aren't predicting hero X against itself.
                    if i != j:
                        #Generate the probablility that any one tree picked this answer as a win
                        result = model.predict_proba(ohe.transform([[str(i) + "-" + str(j)]]))[0].tolist()[0][0]
                        #add results to itself.
                        sum = sum + result
                        #Store in a dict of {hero_id:sum_of_probabilities}
                        results[i] = sum
    #Get the maximum value of all the keys
    max_value = max(results.values());  {key for key, value in results.items() if value == max_value}
    #In the case that we have more than 3 heroes with the same maximum value, just randomly pick 3 from the available options, This shouldnt happen but it does
    if len({key for key, value in results.items() if value == max_value}) >= num_heroes:
        possible_heroes = []
        for key,value in results.items():
            if value == max_value:
                possible_heroes.append(key)
        hero_picks = random.sample(possible_heroes,3)
    #otherwise do the right thing and get the 3 best results from the dictionary and return them.
    else:
        hero_picks = sorted(results, key=results.get, reverse=True)[:num_heroes]
    output_list = heroize(hero_picks)
    return render_template('index.html',hero_list=output_list)



if __name__ == "__main__":
    app.run(debug=True)