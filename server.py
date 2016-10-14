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
from flask import Flask, Response, jsonify, request, json
from sklearn.ensemble.gradient_boosting import QuantileEstimator

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
        assets.append(asset)
        
        
    def sell(self, id, Q):
        for asset in self.assets:
            if asset.id == id:
                asset.sell(Q) #should catch the error somewhere if negative
                self.nav -= asset.price * Q
                if asset.quantity == 0:
                    self.assets.remove(asset)
                return
        raise Error("The asset could not be found in the portfolio.")
        
portfolios = []

######################################################################
# GET INDEX
######################################################################
@app.route('/')
def index():
    return "jsonify(name='My REST API Service', version='1.0', url='/resources')", HTTP_200_OK

######################################################################
# LIST ALL users
######################################################################
@app.route('/api/v1/portfolios', methods=['GET'])
def list_users():
    # YOUR CODE here (remove pass)
    pass

######################################################################
# LIST ALL assets of a user
######################################################################
@app.route('/api/v1/portfolios/<user>', methods=['GET'])
def list_assets():
    # YOUR CODE here (remove pass)
    pass

######################################################################
# RETRIEVE the quantity and total value of an asset in a portfolio
######################################################################
@app.route('/api/v1/portfolios/<user>/<asset_id>', methods=['GET'])
def get_resource(asset_id):
    # YOUR CODE here (remove pass)
    pass

######################################################################
# ADD A NEW user portfolio
######################################################################
@app.route('/api/v1/portfolios', methods=['POST'])
def create_user():
    # Put the asset id and the eventual quantity in the body
    payload = json.loads(request.data)
    if is_valid(payload):
        user = payload['user'])
        for portfolio in portfolios:
            if portfolio.user == user: #user already exists
                message = { 'error' : 'User %s already exists' % user }
                rc = HTTP_409_CONFLICT
                return reply(message, rc)
        #User does not exist yet
        portfolios.append(Portfolio(user))
        rc = HTTP_201_CREATED
    else:
        message = { 'error' : 'Data is not valid' }
        rc = HTTP_400_BAD_REQUEST
    return reply(message, rc)

######################################################################
# ADD A NEW asset
######################################################################
@app.route('/api/v1/portfolios/<user>', methods=['POST'])
def create_asset():
    # Put the asset id and the eventual quantity in the body
    payload = json.loads(request.data)
    if is_valid(payload):
        asset_id = int(payload['asset_id'])
        quantity = int(payload['quantity'])
        if asset_id not in database: #asset_id exists and is associated
            message = { 'error' : 'Asset id does not exist in database' }
            rc = HTTP_400_BAD_REQUEST
        else:
            for portfolio in portfolios:
                if portfolio.user == user:
                    portfolio.buy(asset_id, quantity)
                    rc = HTTP_201_CREATED
                    return reply(message, rc)
            message = { 'error' : 'User not found' }
            rc = HTTP_400_BAD_REQUEST
    else:
        message = { 'error' : 'Data is not valid' }
        rc = HTTP_400_BAD_REQUEST
    return reply(message, rc)

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
#   M A I N
######################################################################
if __name__ == "__main__":
    # Get bindings from the environment
    port = os.getenv('PORT', '5000')
    hostname = os.getenv('HOSTNAME','127.0.0.1')
    redis_port = os.getenv('REDIS_PORT','6379')
    redis_server = redis.Redis(host=hostname, port=int(redis_port))
    app.run(host='0.0.0.0', port=int(port), debug=True)
