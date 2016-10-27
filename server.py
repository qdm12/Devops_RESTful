# Copyright 2016 John J. Rofrano. All Rights Reserved.
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
# https://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.

import os
import redis
from flask import Flask, Response, jsonify, request, json

# Status Codes
HTTP_200_OK = 200
HTTP_201_CREATED = 201
HTTP_204_NO_CONTENT = 204
HTTP_400_BAD_REQUEST = 400
HTTP_404_NOT_FOUND = 404
HTTP_409_CONFLICT = 409

# Create Flask application
app = Flask(__name__)

database = {
            0 : ["commodity", "gold", 1286.59],
            1 : ["real-estate", "NYC real estate index", 16255.18],
            2 : ["commodity", "brent crude oil", 51.45],
            3 : ["fixed income", "US 10Y T-Note", 130.77]
            }

class Asset(object):
    def __init__(self, id, quantity = 0):
        self.id = id
        self.asset_class = database[id][0]
        self.name = database[id][1]
        self.price = database[id][2]
        self.quantity = quantity
        self.nav = self.quantity * self.price
        
    def buy(self, Q):
        self.quantity += Q
        self.nav = self.quantity * self.price
        
    def sell(self, Q):
        if self.quantity - Q < 0:
            raise Error("The quantity of the asset would then be negative")
        self.quantity -= Q
        self.nav = self.quantity * self.price


class Portfolio(object):
    def __init__(self, user): #constructor
        self.user = user
        self.assets = []
        self.nav = 0
       
    def buy(self, id, Q): #This also creates new asset in the portfolio
        for asset in self.assets:
            if asset.id == id:
                # Asset was present in portfolio
                asset.buy(Q)
                self.nav += asset.price * Q
                return
        # Asset was not present in portfolio
        asset = Asset(id, Q)
        self.nav += asset.price * Q
        self.assets.append(asset)
        
    def sell(self, id, Q):
        for asset in self.assets:
            if asset.id == id:
                asset.sell(Q) #should catch the error somewhere if negative
                self.nav -= asset.price * Q
                if asset.quantity == 0:
                    self.assets.remove(asset)
                return
        raise Error("The asset could not be found in the portfolio.")
        
    def serialize(self, url_root):
        return {
            "user" : self.user,
            "numberOfAssets" : len(self.assets),
            "netAssetValue" : self.nav,
            "links" : create_links_for_portfolio(self, url_root)
        }
        
portfolios = []

######################################################################
# GET INDEX
######################################################################
@app.route('/')
def index():
    return app.send_static_file('index.html')

######################################################################
# LIST ALL porfolios
######################################################################
@app.route('/api/v1/portfolios', methods=['GET'])
def list_portfolios():
    """
    GET request at /api/v1/portfolios
    
    Returns all portfolios with form
    {
        "portfolios" : [
            "user" : <user>
            "numberOfAssets" : <number of assets>
            "netAssetValue : <nav>
            "links" : [
                "rel" : "self"
                "href" : <fully-fledged url to list_assets(<user>)>
            ]
        ]...
    }
    """
    return reply({"portfolios" : [p.serialize(request.url_root) for p in portfolios]}, HTTP_200_OK)

######################################################################
# LIST ALL assets of a user
######################################################################
@app.route('/api/v1/portfolios/<user>', methods=['GET'])
def list_assets(user):
    """
    GET request at localhost:5000/api/v1/portfolios/<user>
    """
    for portfolio in portfolios:
        if portfolio.user == user:
            # assuming only one portfolio per user
            return reply({"assets" : [asset.name for asset in portfolio.assets]}, HTTP_200_OK)
    #The user's portfolio does not exist
    return reply({ 'error' : 'User %s does not exist' % user }, HTTP_400_BAD_REQUEST)

######################################################################
# RETRIEVE the quantity and total value of an asset in a portfolio
######################################################################
@app.route('/api/v1/portfolios/<user>/<asset_id>', methods=['GET'])
def get_resource(asset_id):
    # YOUR CODE here (remove pass)
    pass

######################################################################
# RETRIEVE the NAV of a portfolio
######################################################################
@app.route('/api/v1/portfolios/<user>/nav', methods=['GET'])
def get_nav(user):
    """
    GET request at localhost:5000/api/v1/portfolios/<user>/nav
    """
    for portfolio in portfolios:
        if portfolio.user == user:
            return reply({"nav" : portfolio.nav}, HTTP_200_OK)
    return reply({'error' : 'User %s does not exist' % user }, HTTP_404_NOT_FOUND)
    
######################################################################
# ADD A NEW user portfolio
######################################################################
@app.route('/api/v1/portfolios', methods=['POST'])
def create_user():
    """
    POST request at localhost:5000/api/v1/portfolios with this body:
    {
        "user": "john"
    }
    """
    try:
        payload = json.loads(request.data)
    except ValueError:
        return reply({ 'error' : 'Data %s is not valid' % request.data}, HTTP_400_BAD_REQUEST)
    if not is_valid(payload, ['user']):
        return reply({ 'error' : 'Payload %s is not valid' % payload}, HTTP_400_BAD_REQUEST)
    user = payload['user']
    for portfolio in portfolios:
        if portfolio.user == user: #user already exists
            return reply({ 'error' : 'User %s already exists' % user }, HTTP_409_CONFLICT)
    #User does not exist yet
    portfolios.append(Portfolio(user))
    return reply("",HTTP_201_CREATED)

######################################################################
# ADD A NEW asset
######################################################################
@app.route('/api/v1/portfolios/<user>', methods=['POST'])
def create_asset(user):
    """
    POST request at localhost:5000/api/v1/portfolios/<user> with this body:
    {
        "asset_id": 2,
        "quantity": 10
    }
    """
    try:
        payload = json.loads(request.data)
    except ValueError:
        return reply({ 'error' : 'Data %s is not valid' % request.data}, HTTP_400_BAD_REQUEST)
    if not is_valid(payload, ['asset_id','quantity']):
        return reply({ 'error' : 'Payload %s is not valid' % payload}, HTTP_400_BAD_REQUEST)
    asset_id = int(payload['asset_id'])
    quantity = int(payload['quantity'])
    if asset_id not in database: #asset_id exists and is associated
        return reply({ 'error' : 'Asset id %s does not exist in database' % asset_id}, HTTP_400_BAD_REQUEST)
    else:
        for portfolio in portfolios:
            if portfolio.user == user:
                portfolio.buy(asset_id, quantity) #That would act as a PUT in some cases, is this fine ?
                return reply("", HTTP_201_CREATED)
        return reply({ 'error' : 'User %s not found' % user}, HTTP_404_NOT_FOUND)

######################################################################
# UPDATE AN EXISTING resource
######################################################################
@app.route('/api/v1/portfolios/<user>/<asset_id>', methods=['PUT'])
def update_resource():
    # Put the add/sell and quantity in the body
    # YOUR CODE here (remove pass)
    pass

######################################################################
# DELETE an asset from a user's portfolio
######################################################################
@app.route('/api/v1/portfolios/<user>/<asset_id>', methods=['DELETE'])
def delete_asset(id):
    # YOUR CODE here (remove pass)
    pass

######################################################################
# DELETE a user (or its portfolio)
######################################################################
@app.route('/api/v1/portfolios/<user>', methods=['DELETE'])
def delete_user(user):
    # YOUR CODE here (remove pass)
    pass


######################################################################
# UTILITY FUNCTIONS
######################################################################
def create_links_for_portfolio(portfolio, url_root):
    return [
        {
            "rel" : "self",
            "href" : url_root + "api/v1/portfolios/" + portfolio.user
        }
    ]
    
def reply(message, rc):
    response = jsonify(message) #or jsonify?
    response.headers['Content-Type'] = 'application/json'
    response.status_code = rc
    return response
    
def is_valid(data, keys=[]):
    valid = False
    try:
        for k in keys:
            _temp = data[k]
        valid = True
    except KeyError as e:
        app.logger.error('Missing value error: %s', e)
    return valid


######################################################################
#   M A I N
######################################################################
if __name__ == "__main__":
    # Get bindings from the environment
    port = os.getenv('PORT', '5000')
    hostname = os.getenv('HOSTNAME','127.0.0.1')
    redis_port = os.getenv('REDIS_PORT','6379')
    redis_server = redis.Redis(host=hostname, port=int(redis_port))
    app.run(host='0.0.0.0', port=int(port), debug=True)
