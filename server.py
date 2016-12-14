import os
from redis import Redis, ConnectionError
from flask import Flask, jsonify, request, json, Response
from werkzeug.security import generate_password_hash, check_password_hash
from functools import wraps

"""
    server.py
    Center point of Portfolio Management System.
    Example usage: python server.py
    Authors:
        Bhavesh Subhash
        Quentin McGaw{@qm301@nyu.edu}
        Shuang Wang{@sw2553@nyu.edu}
        Zhiyu Feng{@zf499@nyu.edu}
"""

# Status Codes
HTTP_200_OK = 200
HTTP_201_CREATED = 201
HTTP_204_NO_CONTENT = 204
HTTP_400_BAD_REQUEST = 400
HTTP_401_UNAUTHORIZED = 401
HTTP_404_NOT_FOUND = 404
HTTP_409_CONFLICT = 409

# Create Flask application
app = Flask(__name__)
url_version = "/api/v1"
app_name = "Portfolio Management RESTful Service"
app_version = 1.0
redis_server = None
SECURED = True

def check_auth(username, password, admin=False):
    """Checks the credentials provided against the ones stored in Redis.

        It searches for the username key in the Redis database, and then
        compares the hash of the password with the hash of the password 
        stored in the Redis database. If it matches, it returns True.

        Args:
            username (string): Name of the username of administrator.
            password (string): Plaintext password of the username or admin.
            admin (boolean): True if the username is an administrator.

        Returns:
            True or False: Returns True if the user is authorized.
    """
    if admin:
        hash_password_stored = redis_server.hget("admin_password_"+username, "hash_password")
    else:
        hash_password_stored = redis_server.hget("password_"+username, "hash_password")
    if not hash_password_stored:
        return False
    return check_password_hash(hash_password_stored, password)

def requires_auth(f):
    """Prompts the user for the his/her username and password credentials.

        It uses the authorization header of the request and compare the 
        hash of the password received with the hash of the user password
        stored in Redis. Multiple user accounts can be setup in Redis, with
        the RESTful API (using POST to /portfolios).

        Args:
            f (function): Function that requires user authentication.

        Returns:
            f(*args, **kwargs): The function with its original arguments,
                                if authorized.
            Response: Error response with status code 401 if not authorized.
    """
    @wraps(f)
    def decorated(user, *args, **kwargs):
        auth = request.authorization
        if SECURED:
            if not auth or auth.username != user or not check_auth(auth.username, auth.password):
                return Response(
                                'Could not verify your access level for that URL.\n'
                                'You have to login with proper credentials',
                                HTTP_401_UNAUTHORIZED,
                                {'WWW-Authenticate': 'Basic realm="Login Required"'})
        return f(user, *args, **kwargs)
    return decorated

def requires_auth_admin(f):
    """Prompts the user for the admin username and admin password.

        It uses the authorization header of the request and compare the 
        hash of the password received with the hash of the admin password
        stored in Redis. Multiple admin accounts can be setup in Redis.

        Args:
            f (function): Function that requires admin authentication.

        Returns:
            f(*args, **kwargs): The function with its original arguments,
                                if authorized.
            Response: Error response with status code 401 if not authorized.
    """
    @wraps(f)
    def decorated(*args, **kwargs):
        auth = request.authorization
        if SECURED:
            if not auth or not check_auth(auth.username, auth.password, admin=True):
                return Response(
                                'Could not verify your access level for that URL.\n'
                                'You have to login with proper credentials',
                                HTTP_401_UNAUTHORIZED,
                                {'WWW-Authenticate': 'Basic realm="Login Required"'})
        return f(*args, **kwargs)
    return decorated

class NegativeAssetException(Exception):
    """Asset has a negative quantity exception

    """
    pass

class AssetNotFoundException(Exception):
    """Asset not found in database exception

    """
    pass

class RedisConnectionException(Exception):
    """Redis service connection exception.

    """
    pass

class Asset(object):
    """Asset class, basic unit of a Portfolio.

        Attributes:
            id (int): A unique id for this asset type.
            quantity (float): The amount of this asset.
            name (str): Name of this asset.
            price (float): The unit price of this asset.
            asset_class (str): The asset class of this asset.
    """
    def __init__(self, ID, Q = 0):
        """Constructor of the Asset class.

            Args:
                ID (int, str): The unique id of the asset type.
                Q (float, int): The quantity number of assets.

            Raises:
                Exception: The quantity argument can't be negative.
        """
        self.id = int(ID)
        self.quantity = float(Q)
        if self.quantity <= 0:
            raise Exception("Asset object can only be created with a strictly positive a quantity Q.")
        self.asset_class = redis_server.hget("asset_id_"+str(self.id), "class")
        self.name = redis_server.hget("asset_id_"+str(self.id), "name")
        self.price = float(redis_server.hget("asset_id_"+str(self.id), "price"))

    def buy(self, Q):
        """Buys a quantity Q of this asset.

            Args:
                Q (float, int): The quantity to buy (positive).
        """
        self.quantity += Q

    def sell(self, Q):
        """Sells a quantity Q of this asset.

            Args:
                Q (float, int): The quantity to buy (positive).

            Raises:
                NegativeAssetException: if the Asset quantity becomes negative.
        """
        if self.quantity - Q < 0:
            raise NegativeAssetException()
        self.quantity -= Q

    def serialize(self, ID):
        """Serializes this Asset object into a string to be stored into Redis.

            Uses the asset id and its quantity to generate a string for Redis.

            Args:
                ID (int): unique id of the asset type

            Returns:
                serialized_data (str): Two hexadecimal parts joined by ';'.
        """
        id_hex = str(ID).encode("hex")
        q_hex = str(self.quantity).encode("hex")
        serialized_data = id_hex + ";" + q_hex
        return serialized_data

    @staticmethod
    def deserialize(serialized_data):
        """Deserializes the string from Redis and returns an Asset object.

            Determines the asset id and the quantity from the string.
            Fetches the other asset parameters from Redis with the asset id.
            This is a static method.

            Args:
                serialized_data (str): Two hexadecimal parts joined by ';'.

            Returns:
                Asset: Complete Asset object defined by the serialized_data.
        """
        serialized_data = serialized_data.split(";")
        ID = serialized_data[0].decode("hex")
        q = serialized_data[1].decode("hex")
        return Asset(ID, float(q))

    def __eq__(self, other):
        """Equal method, used to tell whether two Asset are the same.

            Compares each attributes of the two Asset objects and returns
            True if these are all equal.

            Args:
                other (Asset): Other Asset object

            Returns:
                isEqual (bool): True if the other Asset has the same
                                values as this one.
        """
        return self.id == other.id and self.asset_class == other.asset_class and self.name == other.name and self.price == other.price and self.quantity == other.quantity

    def __repr__(self):
        """Representation method, used by the str() and by print for example.

            Returns:
                repr (str): String representation of the Asset object.
        """
        return "[id "+str(self.id)+", name "+self.name+", class "+self.asset_class+", quantity "+str(self.quantity)+", price "+str(self.price)+"]"

class Portfolio(object):
    """Portfolio class, a combination of Asset(s) for one user account.

        Attributes:
            user (str): user name owner of the portfolio
            assets (dict[int:Asset]): Assets belonging to the user
            nav (float): Net asset value of the user's portfolio
    """
    def __init__(self, user):
        """Constructor of the Portfolio class.

            Args:
                user (str): The unique id of the asset type.
                Q (float, int): The quantity number of assets.

            Raises:
                Exception: The quantity argument can't be negative.
        """
        self.user = str(user) #only used to serialize and deserialize
        self.assets = dict()
        self.nav = 0

    def buy_sell(self, ID, Q, can_be_created=True):
        """Buys or sells a quantity Q of an asset with id ID.

            Args:
                ID (int): Unique asset id.
                Q (float, int): The quantity to buy (positive) or sell (negative).
                can_be_created (bool): If true, the asset is created if it
                                       does not exist in the portfolio and
                                       if the quantity Q is positive (buy).
                                       If false, an exception is raised if
                                       the asset does not exist in the
                                       portfolio.

            Raises:
                AssetNotFoundException: if asset ID does not exist in the
                                        Redis database or if the asset does
                                        not exist in the portfolio and can't
                                        be created (PUT method).
        """
        if Q > 0:
            if ID not in self.assets: # asset was not present in portfolio
                if not can_be_created:
                    raise AssetNotFoundException()
                self.assets[ID] = Asset(ID, Q)
            else: # asset was present in portfolio
                self.assets[ID].buy(Q)
            self.nav += self.assets[ID].price * Q
        elif Q < 0:
            if ID not in self.assets: # asset was not present in portfolio
                raise AssetNotFoundException()
            else:
                self.assets[ID].sell(-Q) # raises an exception if q becomes negative
                self.nav += self.assets[ID].price * Q
                if self.assets[ID].quantity == 0:
                    del self.assets[ID]

    def remove_asset(self, ID):
        """Removes an asset with id ID from the portfolio.

            Args:
                ID (int): Unique asset id.
        """
        if ID in self.assets:
            self.nav -= self.assets[ID].price * self.assets[ID].quantity
            del self.assets[ID]

    def json_serialize(self, url_root):
        """Prepares the portfolio object to be serialized in JSON.

            Args:
                url_root (str): root of the url

            Returns:
                data (dict): A dictionary illustrating the portfolio for
                             jsonify to produce.
        """
        return {
            "user" : self.user,
            "numberOfAssets" : len(self.assets),
            "netAssetValue" : self.nav,
            "links" : [{"rel" : "self", "href" : url_root[:-1] + url_version + "/portfolios/" + self.user}]
            }

    def serialize(self):
        """Serializes this Portfolio object into a string to be stored
           into Redis.

            Uses the username and the serialized Assets to generate a
            string for Redis.

            Returns:
                serialized_data (str): Two hexadecimal parts joined by ';'.
        """
        user_hex = self.user.encode("hex")
        assets = "#".join([a.serialize(a_id) for a_id, a in self.assets.iteritems()])
        assets_hex = assets.encode("hex")
        serialized_data = user_hex + ";" + assets_hex
        return serialized_data

    @staticmethod
    def deserialize(serialized_data):
        """Deserializes the string from Redis and returns a Portfolio object.

            Determines the assets data and the NAV from the serialized
            assets data retrieved from Redis. This is a static method.

            Args:
                serialized_data (str): Two hexadecimal parts joined by ';'.

            Returns:
                Portfolio: Complete Portfolio object defined by the
                           serialized_data.
        """
        serialized_data = serialized_data.split(";")
        user = serialized_data[0].decode("hex")
        p = Portfolio(user)
        assets_lst = []
        if serialized_data[1]:
            assets_str = serialized_data[1].decode("hex").split("#")
            assets_lst = [Asset.deserialize(asset_str) for asset_str in assets_str]
        for asset in assets_lst:
            p.assets[asset.id] = asset
            p.nav += float(asset.quantity) * float(asset.price)
        return p

    def __eq__(self, other):
        """Equal method, used to tell whether two Portfolio objects are the same.

            Compares each attributes of the two Portfolio objects and returns
            True if these are all equal.

            Args:
                other (Portfolio): Other Portfolio object

            Returns:
                isEqual (bool): True if the other Portfolio has the same
                                attributes' values as this one.
        """
        return self.user == other.user and self.assets == other.assets and self.nav == other.nav

    def __repr__(self):
        """Representation method, used by the str() and by print for example.

            Returns:
                repr (str): String representation of the Portfolio object.
        """
        return "Portfolio details: \n  user: "+self.user+"\n  NAV: "+str(self.nav)+"\n  assets: "+str(self.assets)+"\n"

    def copy(self):
        """Copy method, to create a Portfolio object with the values of this one.

            Returns:
                p (Portfolio): Portfolio object with the same attributes
                               values of this Portfolio object.
        """
        p = Portfolio(self.user)
        p.assets = self.assets
        p.nav = self.nav
        return p


@app.route('/')
def index():
    """Sends the Swagger main HTML page to the client.

        Returns:
            response (Response): HTML content of static/swagger/index.html
    """
    return app.send_static_file('swagger/index.html')

@app.route('/lib/<path:path>')
def send_lib(path):
    """Sends the Swagger javascript files from the lib folder.

        This is uesd by static/swagger/index.html which includes the lib
        folder when executed.

        Returns:
            response (Response): JS content of static/swagger/lib/***.js
    """
    return app.send_static_file('swagger/lib/' + path)

@app.route('/specification/<path:path>')
def send_specification(path):
    """Sends the Swagger JS specification from the specification folder.

        This is uesd by static/swagger/index.html which includes the
        specification JS file when executed.

        Returns:
            response (Response): JS content of
                                 static/swagger/specification/***.*
    """
    return app.send_static_file('swagger/specification/' + path)

@app.route('/images/<path:path>')
def send_images(path):
    """Sends the Swagger image files from the images folder.

        This is uesd by static/swagger/index.html which includes the images
        folder when executed.

        Returns:
            response (Response): PNG content of static/swagger/images/***.png
    """
    return app.send_static_file('swagger/images/' + path)

@app.route('/css/<path:path>')
def send_css(path):
    """Sends the Swagger css files from the css folder.

        This is uesd by static/swagger/index.html which includes the css
        folder when executed.

        Returns:
            response (Response): CSS content of static/swagger/css/***.css
    """
    return app.send_static_file('swagger/css/' + path)

@app.route('/fonts/<path:path>')
def send_fonts(path):
    """Sends the Swagger tff files from the fonts folder.

        This is uesd by static/swagger/index.html which includes the fonts
        folder when executed.

        Returns:
            response (Response): Fonts content of
                                 static/swagger/fonts/***.ttf
    """
    return app.send_static_file('swagger/fonts/' + path)

@app.route(url_version)
def index_api():
    """Sends the name and version of the API to the user in JSON.

        Returns:
            response (Response): JSON containing the app name, version.
    """
    return reply({"name":app_name, "version":app_version, "url":"/portfolios"}, HTTP_200_OK)

@app.route(url_version+"/portfolios", methods=['GET'])
@requires_auth_admin
def list_portfolios():
    """Returns a list of all the Portfolio objects present in Redis.

        Initiated with a GET to /api/v1/portfolios.

        Returns:
            response (Response): A list of portfolios information.
    """
    portfolios_array = []
    for user in redis_server.smembers('list_users'):
        username = redis_server.hget("user_"+user, "name")
        if username:
            data = redis_server.hget("user_"+user, "data")
            portfolio = Portfolio(user) # in case there is no data, but portfolio still exists
            if data:
                portfolio = Portfolio.deserialize(data)
            json_data = portfolio.json_serialize(request.url_root)
            portfolios_array.append(json_data)
    return reply({"portfolios" : portfolios_array}, HTTP_200_OK)

@app.route(url_version+"/portfolios/<user>/assets", methods=['GET'])
@requires_auth
def list_assets(user):
    """Returns a list of all the assets of a portfolio.

        Initiated with a GET to /api/v1/portfolios/<user>/assets.

        Returns:
            response (Response): A list of assets (id and name) OR an
                                 error message.
    """
    username = redis_server.hget("user_"+user,"name")
    if not username:
        return reply({'error' : 'User {0} not found'.format(user)}, HTTP_404_NOT_FOUND)
    data = redis_server.hget("user_"+user,"data")
    portfolio = Portfolio(user)
    if data:
        portfolio = Portfolio.deserialize(data)
    return reply({'assets' : [{'id' : asset.id, 'name' : asset.name} for asset in portfolio.assets.itervalues()]}, HTTP_200_OK)

@app.route(url_version+"/portfolios/<user>/assets/<asset_id>", methods=['GET'])
@requires_auth
def get_asset(user, asset_id):
    """Returns the details of an asset of a Portfolio.

        Initiated with a GET to /api/v1/portfolios/<user>/assets/<asset_id>.

        Returns:
            response (Response): Contains the name, quantity and total
                                 value of an asset OR an error message.
    """
    username = redis_server.hget("user_"+user,"name")
    if not username:
        return reply({'error' : 'User {0} not found'.format(user)}, HTTP_404_NOT_FOUND)
    data = redis_server.hget("user_"+user,"data")
    if not data:
        return reply({'error' : 'The portfolio of user {0} has no data!'.format(user)}, HTTP_404_NOT_FOUND)
    portfolio = Portfolio.deserialize(data)
    asset_id = int(asset_id)
    if asset_id not in portfolio.assets:
        return reply({'error' : 'Asset with id {0} does not exist in this portfolio'.format(asset_id)}, HTTP_404_NOT_FOUND)
    return reply({'name' : portfolio.assets[asset_id].name, 'quantity' : portfolio.assets[asset_id].quantity, 'value' : portfolio.assets[asset_id].quantity * portfolio.assets[asset_id].price}, HTTP_200_OK)

@app.route(url_version+"/portfolios/<user>/nav", methods=['GET'])
@requires_auth
def get_nav(user):
    """Returns the Net Asset Value (NAV) of a Portfolio.

        Initiated with a GET to /api/v1/portfolios/<user>/nav.

        Returns:
            response (Response): Contains the NAV value.
    """
    username = redis_server.hget("user_"+user,"name")
    if not username:
        return reply({'error' : 'User {0} not found'.format(user)}, HTTP_404_NOT_FOUND)
    data = redis_server.hget("user_"+user,"data")
    portfolio = Portfolio(user)
    if data:
        portfolio = Portfolio.deserialize(data)
    return reply({"nav" : portfolio.nav}, HTTP_200_OK)

@app.route(url_version+"/portfolios", methods=['POST'])
@requires_auth_admin
def create_user():
    """Creates a user

        Initiated with a POST to /api/v1/portfolios with
        a body {"user": "john", "password":"pass123"}
        ONLY WORKS THROUGH HTTPS

        Returns:
            response (Response): Returns "" or an error message.
    """
    try:
        payload = json.loads(request.data)
    except ValueError:
        return reply({'error' : 'Data {0} is not valid'.format(request.data)}, HTTP_400_BAD_REQUEST)
    if not is_valid(payload, ['user']):
        return reply({'error' : 'Payload {0} is not valid'.format(payload)}, HTTP_400_BAD_REQUEST)
    if SECURED:
        if not is_valid(payload, ['password']):
            return reply({'error' : 'Payload is missing the password {0} (SECURED mode on)'.format(payload)}, HTTP_400_BAD_REQUEST)
    user = payload['user']
    if not redis_server.hget("user_"+user,"name"):
        redis_server.sadd('list_users', user) # Set of users
        redis_server.hmset("user_"+user, {"name": user})
        if SECURED:
            hash_password = generate_password_hash(payload['password'])
            redis_server.hmset("password_"+user, {"hash_password":hash_password})
        return reply("", HTTP_201_CREATED)
    return reply({'error' : 'User {0} already exists'.format(user)}, HTTP_409_CONFLICT)

@app.route(url_version+"/portfolios/<user>/assets", methods=['POST'])
@requires_auth
def create_asset(user):
    """Creates an asset in a user's Portfolio.

        Initiated with a POST to /api/v1/portfolios/<user>/assets with
        a body {"asset_id": 2, "quantity": 10}

        Returns:
            response (Response): Returns "" or an error message.
    """
    try:
        payload = json.loads(request.data)
    except ValueError:
        return reply({'error' : 'Data {0} is not valid'.format(request.data)}, HTTP_400_BAD_REQUEST)
    if not is_valid(payload, ['asset_id','quantity']):
        return reply({'error' : 'Payload {0} is not valid'.format(payload)}, HTTP_400_BAD_REQUEST)
    quantity = float(payload['quantity'])
    if quantity < 0:
        return reply({'error' : 'Quantity value must be positive'}, HTTP_400_BAD_REQUEST)
    asset_id = int(payload['asset_id'])
    ID = redis_server.hget("asset_id_"+str(asset_id),"id")
    if ID != 0 and not ID:
        return reply({'error' : 'Asset id {0} does not exist in database'.format(asset_id)}, HTTP_400_BAD_REQUEST)
    username = redis_server.hget("user_"+user,"name")
    if not username:
        return reply({'error' : 'User {0} not found'.format(user)}, HTTP_404_NOT_FOUND)
    data = redis_server.hget("user_"+user, "data")
    portfolio = Portfolio(user)
    if data:
        portfolio = Portfolio.deserialize(data)
    if asset_id in portfolio.assets:
        return reply({'error' : 'Asset with id {0} already exists in portfolio.'.format(asset_id)}, HTTP_409_CONFLICT)
    portfolio.buy_sell(asset_id, quantity)
    data = portfolio.serialize()
    redis_server.hmset("user_"+user, {"data": data})
    return reply("", HTTP_201_CREATED)

@app.route(url_version+"/portfolios/<user>/assets/<asset_id>", methods=['PUT'])
@requires_auth
def update_asset(user, asset_id):
    """Creates an asset in a user's Portfolio.

        Initiated with a PUT to /api/v1/portfolios/<user>/assets/<asset_id>
        with a body {"quantity": -4.2}

        Returns:
            response (Response): Returns "" or an error message.
    """
    try:
        payload = json.loads(request.data)
    except ValueError:
        return reply({'error' : 'Data {0} is not valid'.format(request.data)}, HTTP_400_BAD_REQUEST)
    if not is_valid(payload, ['quantity']):
        return reply({'error' : 'Payload {0} is not valid'.format(payload)}, HTTP_400_BAD_REQUEST)
    try:
        asset_id = int(asset_id)
    except ValueError:
        return reply({'error' : 'The asset_id {0} is not an integer'.format(asset_id)}, HTTP_400_BAD_REQUEST)
    quantity = int(payload['quantity'])
    username = redis_server.hget("user_"+user,"name")
    if not username:
        return reply({'error' : 'User {0} not found'.format(user)}, HTTP_404_NOT_FOUND)
    data = redis_server.hget("user_"+user,"data")
    if not data:
        return reply({'error' : 'No data associated with user {0}'.format(user)}, HTTP_404_NOT_FOUND)
    portfolio = Portfolio.deserialize(data)
    try:
        portfolio.buy_sell(asset_id, quantity, can_be_created=False)
    except AssetNotFoundException:
        return reply({'error' : 'Asset with id {0} was not found in the portfolio of {1}.'.format(asset_id, user)}, HTTP_404_NOT_FOUND)
    except NegativeAssetException:
        return reply({'error' : 'Selling {0} units of the asset with id {1} in the portfolio of {2} would result in a negative quantity. The operation was aborted.'.format(-quantity, asset_id, user)}, HTTP_400_BAD_REQUEST)
    data = portfolio.serialize()
    redis_server.hmset("user_"+user,{"data": data})
    return reply("", HTTP_200_OK)

@app.route(url_version+"/portfolios/<user>/assets/<asset_id>", methods=['DELETE'])
@requires_auth
def delete_asset(user, asset_id):
    """Deletes an asset from a user's Portfolio.

        Initiated with a DELETE to /api/v1/portfolios/<user>/assets/<asset_id>

        Returns:
            response (Response): Returns "" with status HTTP_204_NO_CONTENT.
    """
    username = redis_server.hget("user_"+user,"name")
    if username:
        data = redis_server.hget("user_"+user,"data")
        if data:
            portfolio = Portfolio.deserialize(data)
            portfolio.remove_asset(int(asset_id)) #removes or does nothing if no asset
            data = portfolio.serialize()
            redis_server.hmset("user_"+user,{"data": data})
    return reply("", HTTP_204_NO_CONTENT)

@app.route(url_version+"/portfolios/<user>", methods=['DELETE'])
@requires_auth_admin
def delete_user(user):
    """Deletes a user.

        Initiated with a DELETE to /api/v1/portfolios/<user>.

        Returns:
            response (Response): Returns "" with status HTTP_204_NO_CONTENT.
    """
    username = redis_server.hget("user_"+user,"name")
    if username:
        redis_server.hdel("user_"+username, ["name","data"])
        redis_server.delete("user_"+username)
        redis_server.srem('list_users', user)
    return reply("", HTTP_204_NO_CONTENT)


######################################################################
# UTILITY FUNCTIONS
######################################################################
def reply(message, rc):
    """Generates a JSON Response object from a message and a response code.

        Args:
            message (str): Message to be sent in the Response.
            rc (int): Response status code

        Returns:
            response (Response): Returns "{message}" with
                                 status code HTTP_204_NO_CONTENT.
    """
    response = jsonify(message)
    response.headers['Content-Type'] = 'application/json'
    response.status_code = rc
    return response

def is_valid(data, keys=[]):
    """Verifies the payload received contains all the necessary elements.

        Checks that every necessary key is present in the payload.

        Args:
            data (dict): Parsed JSON payload.
            keys (list): List of required dictionary keys.

        Returns:
            isValid (bool): True if it is valid, otherwise False.
    """
    for k in keys:
        if k not in data:
            #app.logger.error('Missing key in data: {0}'.format(k))
            return False
    return True

class Credentials(object):
    """Credentials class, just a structure to store credentials elements.

        Attributes:
            environment (str): String identifying the OS environment.
            host (str): Hostname on which the Redis serice is running.
            port (int): Port on which Redis is running.
            password (None, string):  Password for accessing Redis on Bluemix.
            swagger_host (string): URL to access the Swagger UI.
    """
    def __init__(self, environment, host, port, password, swagger_host):
        """Constructor of the Credentials class.

            Args:
                environment (str): String identifying the OS environment.
                host (str): Hostname on which the Redis serice is running.
                port (int): Port on which Redis is running.
                password (None, string):  Password for accessing Redis on Bluemix.
                swagger_host (string): URL to access the Swagger UI.
        """
        self.environment = environment
        self.host = host
        self.port = port
        self.password = password
        self.swagger_host = swagger_host

    def __eq__(self, other):
        """Equal method, used to tell whether two Credentials are the same.

            Compares each attributes of the two Credentials objects and
            returns True if these are all equal.

            Args:
                other (Credentials): Other Credentials object

            Returns:
                isEqual (bool): True if the other Credentials has the same
                                values as this one.
        """
        return self.environment == other.environment and self.host == other.host and self.port == other.port and self.password == other.password and self.swagger_host == other.swagger_host

def determine_credentials():
    """Determines the environment, the Redis credentials and the Swagger URL.

        This uses various conditions to deduct the environment running the
        service (Vagrant, Container, Bluemix...). Depending on the finding,
        different Redis credentials and hostnames are assigned to a
        Credentials object which is returned at the end.

        Returns:
            creds (Credentials): A full consistent Credentials object.
    """
    if 'VCAP_SERVICES' in os.environ:
        services = json.loads(os.environ['VCAP_SERVICES'])
        redis_creds = services['rediscloud'][0]['credentials']
        creds = Credentials("Bluemix", redis_creds['hostname'], int(redis_creds['port']), redis_creds['password'], "portfoliomgmt.mybluemix.net")
        if os.path.isfile("/.dockerenv"):
            creds.environment = "Docker running in Bluemix"
            creds.swagger_host = "portfoliocontainer.mybluemix.net"
        return creds
    if os.path.isfile("/.dockerenv"):
        return Credentials("Docker running in Vagrant", "redis", 6379, None, "localhost:5000")
    return Credentials("Vagrant", "127.0.0.1", 6379, None, "localhost:5000")

def update_swagger_specification(swagger_host):
    """Generates the JS Swagger from the JSON and update the "host" variable.

        It reads the JSON Swagger specification to create the JS Swagger
        specification in the same directory where the JSON content is
        assigned to the variable spec and where the "host":"...." is
        replaced by the swagger_host provided (dynamic hostname).

        Args:
            swagger_host (str): URL to access the swagger UI.
    """
    spec_dir = os.path.dirname(__file__)
    if len(spec_dir): # Not docker container
        spec_dir += "/"
    spec_dir += "static/swagger/specification/"
    with open(spec_dir + "portfolioMgmt.json") as f:
        spec_lines = f.readlines()
    with open(spec_dir + "portfolioMgmt.js", 'w') as f:
        f.write("var spec = ")
        for i in range(len(spec_lines)):
            if '"host"' in spec_lines[i] and i < 20:
                pos = spec_lines[i].find('"host"')
                spec_lines[i] = spec_lines[i][:pos+6] + ': "'+swagger_host+'",\n'
            f.write(spec_lines[i])
        f.write(";")

def init_redis(hostname, port, password):
    """Initializes the connection to the Redis server and checks for errors.

        Args:
            hostname (str): Hostname of the Redis service.
            port (int): Port of the Redis service.
            password (None, str): Password to access the Redis service.

        Raises:
            RedisConnectionException: If Redis can't be pinged.
    """
    global redis_server
    redis_server = Redis(host=hostname, port=port, password=password)
    try:
        redis_server.ping()
    except ConnectionError:
        raise RedisConnectionException()
    fill_database_assets() - Used for new Vagrant machines where Redis is empty.
    if SECURED:
        admin_username = "admin"
        admin_password = "admin_password"
        hash_password = generate_password_hash(admin_password)
        redis_server.hmset("admin_password_"+admin_username, {"hash_password":hash_password})

def fill_database_assets():
    redis_server.hmset("asset_id_0", {"id": 0,"name":"gold","price":1286.59,"class":"commodity"})
    redis_server.hmset("asset_id_1", {"id": 1,"name":"NYC real estate index","price":16255.18,"class":"real-estate"})
    redis_server.hmset("asset_id_2", {"id": 2,"name":"brent crude oil","price":51.45,"class":"commodity"})
    redis_server.hmset("asset_id_3", {"id": 3,"name":"US 10Y T-Note","price":130.77,"class":"fixed income"})

# def fill_database_fakeusers():
    # redis_server.hmset("user_john", {"name": "john","data":""})
    # redis_server.hmset("user_jeremy", {"name": "jeremy","data":""})
    # redis_server.sadd('list_users', "john")
    # redis_server.sadd('list_users', "jeremy")
    # redis_server.hmset("user_john", {"name": "john","data":"6a6f686e;33303b3335"})
    # redis_server.hmset("user_jeremy", {"name": "jeremy","data":"6a6572656d79;33303b3335"})

######################################################################
#   M A I N
######################################################################
if __name__ == "__main__":
    creds = determine_credentials()
    try:
        init_redis(creds.host, creds.port, creds.password)
    except RedisConnectionException:
        print("The server could not connect to Redis. Stopping...\n\n")
        exit(1)
    update_swagger_specification(creds.swagger_host)
    port = os.getenv('PORT', '5000')
    app.run(host='0.0.0.0', port=int(port), debug=True)
