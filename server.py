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

           
class NegativeAssetException(Exception):
    pass
    
class AssetNotFoundException(Exception):
    pass

class Asset(object):
    def __init__(self, id, quantity = 0):
        self.id = int(id)
        self.asset_class = redis_server.hget("asset_type"+str(self.id),"type")
        self.name = redis_server.hget("asset_type"+str(self.id),"name")
        self.price = float(redis_server.hget("asset_type"+str(self.id),"value")) 
        self.quantity = int(quantity)
        self.nav = float(self.quantity) * float(self.price)
        
    def buy(self, Q):
        self.quantity += int(Q)
        self.nav = self.quantity * self.price
        
    def sell(self, Q):
        if self.quantity - Q < 0:
            raise NegativeAssetException()
        self.quantity -= Q
        self.nav = self.quantity * self.price
        
    def serialize(self,id):
        #This generates a string from the Asset object (id, quantity parameters)
        id_hex = str(id).encode("hex")
        q_hex = str(self.quantity).encode("hex")
        serialized_data = id_hex + ";" + q_hex
        return serialized_data
    
    @staticmethod
    def deserialize(serialized_data): #This takes the string generated from serialize and returns an Asset object
        if serialized_data is None:
            return
        serialized_data = serialized_data.split(";")
        id = serialized_data[0].decode("hex")
        q = serialized_data[1].decode("hex")
        return Asset(id, q)
        


class Portfolio(object):
    def __init__(self, user): #constructor
        self.user = str(user) #only used to serialize and deserialize
        self.assets = dict()
        self.nav = 0
       
    def buy(self, id, Q): #This also creates new asset in the portfolio
        if Q == 0:
            return
        try:
            asset = self.assets[id]
        except KeyError: # Asset was not present in portfolio
            asset = Asset(id, Q)
            self.assets[id] = asset
        else: # Asset was present in portfolio
            self.assets[id].buy(Q)
        self.nav += self.assets[id].price * Q 
        
    def sell(self, id, Q):
        if Q == 0:
            return
        try:
            asset = self.assets[id]
        except KeyError: # Asset was not present in portfolio
            raise AssetNotFoundException()
        else:
            self.assets[id].sell(Q) #raises an error if q becomes negative
            self.nav -= self.assets[id].price * Q
            if self.assets[id].quantity == 0:
                del self.assets[id]
        
    def buy_sell(self, id, Q):
        if Q < 0:
            self.sell(id, -Q)
        else:
            self.buy(id, Q)
        
    def remove_asset(self, id):
        del self.assets[id]
        
    def json_serialize(self, user, url_root):
        return {
            "user" : user,
            "numberOfAssets" : len(self.assets),
            "netAssetValue" : self.nav,
            "links" : [{"rel" : "self", "href" : url_root + "api/v1/portfolios/" + user}]
            }
        
    def serialize(self):
        #This generates a string from the Portfolio object (user, and assets parameters)
        user_hex = self.user.encode("hex")
        assets = "#".join([a.serialize(a_id) for a_id, a in self.assets.iteritems()])
        assets_hex = assets.encode("hex")        
        serialized_data = user_hex + ";" + assets_hex
        return serialized_data
    
    @staticmethod
    def deserialize(serialized_data):
        #This takes the string generated from serialize and returns a Portfolio object
        serialized_data = serialized_data.split(";")
        user = serialized_data[0].decode("hex")
        p = Portfolio(user)
        assets_str = serialized_data[1].decode("hex").split("#")
        assets_lst = [Asset.deserialize(asset_str) for asset_str in assets_str]
        for asset in assets_lst:
            p.assets[asset.id] = asset
            p.nav += float(asset.quantity) * float(asset.price)
        return p
        
######################################################################
# GET INDEX
######################################################################
@app.route('/')
def index():
    return app.send_static_file('swagger/index.html')
    
@app.route('/js/<path:path>')
def send_js(path):
    return app.send_static_file('swagger/js/' + path)
    
@app.route('/images/<path:path>')
def send_img(path):
    return app.send_static_file('swagger/images/' + path)
    
@app.route('/css/<path:path>')
def send_css(path):
    return app.send_static_file('swagger/css/' + path)

######################################################################
# LIST ALL portfolios
######################################################################
@app.route('/api/v1/portfolios', methods=['GET'])
def list_portfolios():
    """
    GET request at /api/v1/portfolios
    """
    portfolios_array = []
    portfolio_dict = redis_server.smembers('userlist')
    for user in portfolio_dict:
        username = redis_server.hget(user,"name")
        if username is not None:
            data = redis_server.hget(user,"data")
            portfolio = Portfolio(user)
            if data is not None:
                portfolio = Portfolio.deserialize(data)
            json_data = portfolio.json_serialize(user, request.url_root)
            portfolios_array.append(json_data)
    return reply({"portfolios" : portfolios_array}, HTTP_200_OK)

######################################################################
# LIST ALL assets of a user
######################################################################
@app.route('/api/v1/portfolios/<user>/assets', methods=['GET'])
def list_assets(user):
    """
    GET request at localhost:5000/api/v1/portfolios/<user>/assets
    """
    username = redis_server.hget(user,"name")
    if username is None:
        return reply({'error' : 'User {0} not found'.format(user)}, HTTP_404_NOT_FOUND)
    data = redis_server.hget(user,"data")
    portfolio = Portfolio(user)
    if data is not None:
        portfolio = Portfolio.deserialize(data)
    return reply({'assets' : [{'id' : asset.id, 'name' : asset.name} for asset in portfolio.assets.itervalues()]}, HTTP_200_OK)
        
######################################################################
# RETRIEVE the quantity and total value of an asset in a portfolio
######################################################################
@app.route('/api/v1/portfolios/<user>/assets/<asset_id>', methods=['GET'])
def get_asset(user, asset_id):
    """
    GET request at localhost:5000/api/v1/portfolios/<user>/assets/<asset_id>
    """
    username = redis_server.hget(user,"name")
    if username is None:
        return reply({'error' : 'User {0} not found'.format(user)}, HTTP_404_NOT_FOUND)
    data = redis_server.hget(user,"data")
    portfolio = Portfolio(user)
    if data is not None:
        portfolio = Portfolio.deserialize(data)
    try:
        asset = portfolio.assets[int(asset_id)]
    except KeyError:
        return reply({'error' : 'Asset with id %s does not exist in this portfolio' % asset_id }, HTTP_404_NOT_FOUND)
    return reply({'name' : asset.name, 'quantity' : asset.quantity, 'value' : asset.nav}, HTTP_200_OK)
        

######################################################################
# RETRIEVE the NAV of a portfolio
######################################################################
@app.route('/api/v1/portfolios/<user>/nav', methods=['GET'])
def get_nav(user):
    """
    GET request at localhost:5000/api/v1/portfolios/<user>/nav
    """
    username = redis_server.hget(user,"name")
    if username is None:
        return reply({'error' : 'User {0} not found'.format(user)}, HTTP_404_NOT_FOUND)
    data = redis_server.hget(user,"data")
    portfolio = Portfolio(user)
    if data is not None:
        portfolio = Portfolio.deserialize(data)
    return reply({"nav" : portfolio.nav}, HTTP_200_OK)

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
        return reply({'error' : 'Data {0} is not valid'.format(request.data)}, HTTP_400_BAD_REQUEST)
    if not is_valid(payload, ['user']):
        return reply({'error' : 'Payload %s is not valid'.format(payload)}, HTTP_400_BAD_REQUEST)
    user = payload['user']
    username = redis_server.hget(user,"name")
    if username is None:
        ##Set of users
        redis_server.sadd('userlist',user)
        
        ##Create a portfolio and save
        portfolio = Portfolio(user)
        redis_server.hmset(user,{'name': user})
        return reply("",HTTP_201_CREATED)
    return reply({'error' : 'User {0} already exists'.format(user)}, HTTP_409_CONFLICT)

######################################################################
# ADD A NEW asset
######################################################################
@app.route('/api/v1/portfolios/<user>/assets', methods=['POST'])
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
        return reply({'error' : 'Data %s is not valid' % request.data}, HTTP_400_BAD_REQUEST)
    if not is_valid(payload, ['asset_id','quantity']):
        return reply({'error' : 'Payload %s is not valid' % payload}, HTTP_400_BAD_REQUEST)
    asset_id = int(payload['asset_id'])
    quantity = int(payload['quantity'])
    id = redis_server.hget("asset_type"+str(asset_id),"id")
    if id is None: #asset_id does not exist
        return reply({'error' : 'Asset id %s does not exist in database' % asset_id}, HTTP_400_BAD_REQUEST)
    username = redis_server.hget(user,"name")
    if username is None:
        return reply({'error' : 'User {0} not found'.format(user)}, HTTP_404_NOT_FOUND)
    data = redis_server.hget(user,"data")
    if data is None:
        return reply({'error' : 'No data associated to user {0}'.format(user)}, HTTP_404_NOT_FOUND)
    portfolio = Portfolio.deserialize(data)
    if asset_id in portfolio.assets:
        return reply({'error' : 'Asset with id {0} already exists in portfolio.'.format(asset_id)}, HTTP_409_CONFLICT)
    portfolio.buy(asset_id, quantity)
    data = portfolio.serialize()
    redis_server.hmset(user,{'data': data})
    return reply("", HTTP_201_CREATED)

######################################################################
# UPDATE AN EXISTING resource
######################################################################
@app.route('/api/v1/portfolios/<user>/assets/<asset_id>', methods=['PUT'])
def update_asset(user, asset_id):
    try:
        payload = json.loads(request.data)
    except ValueError:
        return reply({'error' : 'Data %s is not valid' % request.data}, HTTP_400_BAD_REQUEST)
    if not is_valid(payload, ['quantity']):
        return reply({'error' : 'Payload %s is not valid' % payload}, HTTP_400_BAD_REQUEST)
    try:
        asset_id = int(asset_id)
    except ValueError:
        return reply({'error' : 'The asset_id %s is not an integer' % asset_id}, HTTP_400_BAD_REQUEST)
    quantity = int(payload['quantity'])
    username = redis_server.hget(user,"name")
    if username is None:
        return reply({'error' : 'User {0} not found'.format(user)}, HTTP_404_NOT_FOUND)
    data = redis_server.hget(user,"data")
    if data is None:
        return reply({'error' : 'No data associated with user {0}'.format(user)}, HTTP_404_NOT_FOUND)
    portfolio = Portfolio.deserialize(data)
    try:
        portfolio.buy_sell(asset_id, quantity)
    except AssetNotFoundException:
        return reply({'error' : 'Asset with id {0} was not found in the portfolio of {1}.'.format(asset_id, user)}, HTTP_404_NOT_FOUND)
    except NegativeAssetException:
        return reply({'error' : 'Selling {0} units of the asset with id {1} in the portfolio of {2} would result in a negative quantity. The operation was aborted.'.format(-quantity, asset_id, user)}, HTTP_400_BAD_REQUEST)
    data = portfolio.serialize()
    redis_server.hmset(user,{'data': data})
    return reply("", HTTP_200_OK)

######################################################################
# DELETE an asset from a user's portfolio
######################################################################
@app.route('/api/v1/portfolios/<user>/assets/<asset_id>', methods=['DELETE'])
def delete_asset(user, asset_id):
    username = redis_server.hget(user,"name")
    if username is not None:
        data = redis_server.hget(user,"data")
        if data is not None:
            portfolio = Portfolio.deserialize(data)
            portfolio.remove_asset(int(asset_id)) #removes or does nothing if no asset
            data = portfolio.serialize()
            redis_server.hmset(user,{'data': data})
    return reply("", HTTP_204_NO_CONTENT)

######################################################################
# DELETE a user (or its portfolio)
######################################################################
@app.route('/api/v1/portfolios/<user>', methods=['DELETE'])
def delete_user(user):
    username = redis_server.hget(user,"name")
    if username is not None:
        redis_server.hdel(username, {"name","data"})
        redis_server.delete(username)
        redis_server.srem('userlist', user)
    return reply("", HTTP_204_NO_CONTENT)


######################################################################
# UTILITY FUNCTIONS
######################################################################   
def reply(message, rc):
    response = jsonify(message)
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

# Initialize Redis
def init_redis(hostname, port, password):
    # Connect to Redis Server
    global redis_server
    redis_server = redis.Redis(host=hostname, port=port, password=password)
    if not redis_server:
        print '*** FATAL ERROR: Could not conect to the Redis Service'
        exit(1)
    ## Initialize Asset types
    redis_server.hmset("asset_type0",{"id": 0,"name":"gold","value":1286.59,"type":"commodity"})
    redis_server.hmset("asset_type1",{"id": 1,"name":"NYC real estate index","value":16255.18,"type":"real-estate"})
    redis_server.hmset("asset_type2",{"id": 2,"name":"brent crude oil","value":51.45,"type":"commodity"})
    redis_server.hmset("asset_type3",{"id": 3,"name":"US 10Y T-Note","value":130.77,"type":"fixed income"})
    redis_server.sadd("assetTypes",{"asset_type0","asset_type1","asset_type2","asset_type3"})

######################################################################
#   M A I N
######################################################################
if __name__ == "__main__":
    # Get the crdentials from the Bluemix environment
    if 'VCAP_SERVICES' in os.environ:
        VCAP_SERVICES = os.environ['VCAP_SERVICES']
        services = json.loads(VCAP_SERVICES)
        redis_creds = services['rediscloud'][0]['credentials']
        # pull out the fields we need
        redis_hostname = redis_creds['hostname']
        redis_port = int(redis_creds['port'])
        redis_password = redis_creds['password']
    else:
        redis_hostname = '127.0.0.1'
        redis_port = 6379
        redis_password = None
    
    init_redis(redis_hostname, redis_port, redis_password)
    port = os.getenv('PORT', '5000')
    app.run(host='0.0.0.0', port=int(port), debug=True)
