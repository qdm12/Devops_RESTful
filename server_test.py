import unittest
import server
import json

# Status Codes
HTTP_200_OK = 200
HTTP_201_CREATED = 201
HTTP_204_NO_CONTENT = 204
HTTP_400_BAD_REQUEST = 400
HTTP_404_NOT_FOUND = 404
HTTP_409_CONFLICT = 409
url_version = "/api/v1"

class FakeRedisServer(object):
    def __init__(self, database=None):
        """ database is a dict of a dict:
        * key 'asset_id_0' and value {"id": 0,"name":"gold","value":1286.59,"class":"commodity"}
            or
        * key 'user_john' and value {"name": "john","data":"6a6f686e;33303b3335"}
            or
        * key 'list_users' and value set("john", ...)
        """
        self.database = database
        
    def hget(self, key, field):
        """
        * key "asset_id_2" and field "id"/"name"/"price"/"class"
            or
        * key "user_john" and field "name"/"data"
        """
        if key not in self.database:
            return []
        return self.database[key][field]
    
    def hmset(self, key, dictionary):
        if key not in self.database:
            self.database[key] = dict()
        for subkey in dictionary:
            self.database[key][subkey] = dictionary[subkey]
            
    def hdel(self, key, dictionary):
        for subkey in dictionary:
            del self.database[key][subkey]
    
    def smembers(self, key="list_users"):
        if key not in self.database:
            return set()
        return self.database[key]
    
    def sadd(self, key="list_users", user="john"):
        if key not in self.database:
            self.database[key] = set()
        self.database[key].add(user)
    
    def srem(self, key="list_users", user="john"):
        self.database[key].remove(user)
        
    def delete(self, key):
        del self.database[key]
        
    def ping(self):
        raise server.ConnectionError()

class NegativeAssetException(unittest.TestCase):
    def test_exception(self):
        with self.assertRaises(server.NegativeAssetException):
            raise server.NegativeAssetException()
        
class AssetNotFoundException(unittest.TestCase):
    def test_exception(self):
        with self.assertRaises(server.AssetNotFoundException):
            raise server.AssetNotFoundException()
        
class Asset(unittest.TestCase):   
    def test_init(self):
        database = dict()
        database["asset_id_1"] = {"id": 1,"name":"NYC real estate index","price":16255.18,"class":"real-estate"}
        server.redis_server = FakeRedisServer(database)
        ID = "1"
        Q = 5
        asset = server.Asset(ID, Q)
        self.assertEquals(asset.id, 1, "Asset id does not match expected result")
        self.assertEquals(asset.asset_class, "real-estate", "Asset class does not match expected result")
        self.assertEquals(asset.name, "NYC real estate index", "Asset name does not match expected result")
        self.assertEquals(asset.price, 16255.18, "Asset price does not match expected result")
        self.assertEquals(asset.quantity, 5, "Asset quantity does not match expected result")
        
    def test_eq(self):
        database = dict()
        database["asset_id_1"] = {"id": 1,"name":"NYC real estate index","price":16255.18,"class":"real-estate"}
        server.redis_server = FakeRedisServer(database)
        ID = "1"
        Q = 5
        asset1 = server.Asset(ID, Q)
        asset2 = server.Asset(ID, Q)
        self.assertTrue(asset1 == asset2)
        
    def test_repr(self):
        database = dict()
        database["asset_id_1"] = {"id": 1,"name":"NYC real estate index","price":16255.18,"class":"real-estate"}
        server.redis_server = FakeRedisServer(database)
        ID = "1"
        Q = 5
        asset = server.Asset(ID, Q)
        self.assertEquals(str(asset), "[id 1, name NYC real estate index, class real-estate, quantity 5.0, price 16255.18]")

    def test_init_zero_quantity(self):
        ID = "1"
        Q = 0
        with self.assertRaises(Exception):
            _ = server.Asset(ID, Q)
        
    def test_init_neg_quantity(self):
        ID = "1"
        Q = -5
        with self.assertRaises(Exception):
            _ = server.Asset(ID, Q)
        
    def test_buy(self):
        database = dict()
        database["asset_id_1"] = {"id": 1,"name":"NYC real estate index","price":16255.18,"class":"real-estate"}
        server.redis_server = FakeRedisServer(database)
        ID = "1"
        Q = 5.5
        asset = server.Asset(ID, Q)
        asset.buy(17)
        self.assertEquals(asset.quantity, 22.5, "Asset new quantity does not match expected result")
        
    def test_sell(self):
        database = dict()
        database["asset_id_1"] = {"id": 1,"name":"NYC real estate index","price":16255.18,"class":"real-estate"}
        server.redis_server = FakeRedisServer(database)
        ID = "1"
        Q = 5.5
        asset = server.Asset(ID, Q)
        asset.sell(1.25)
        self.assertEquals(asset.quantity, 4.25, "Asset new quantity does not match expected result")
        
    def test_sell_neg(self):
        database = dict()
        database["asset_id_1"] = {"id": 1,"name":"NYC real estate index","price":16255.18,"class":"real-estate"}
        server.redis_server = FakeRedisServer(database)
        ID = "1"
        Q = 5.5
        asset = server.Asset(ID, Q)
        with self.assertRaises(server.NegativeAssetException):
            asset.sell(6.2)
        self.assertEquals(asset.quantity, Q)
        
    def test_serialize(self):
        ID = "1"
        Q = 5.5
        asset = server.Asset(ID, Q)
        data = asset.serialize(ID)
        self.assertEquals(data, "31;352e35", "Serialized data does not match expected result")
        
    def test_deserialize(self):
        database = dict()
        database["asset_id_1"] = {"id": 1,"name":"NYC real estate index","price":16255.18,"class":"real-estate"}
        server.redis_server = FakeRedisServer(database)
        data = "31;352e35"
        asset = server.Asset.deserialize(data)
        self.assertEquals(asset, server.Asset("1", 5.5))
   
class FakeAsset(object):
    def __init__(self, ID, Q):
        self.id = int(ID)
        self.quantity = Q
        self.price = 2.5
        self.asset_class = None
        self.name = None
        self.nav = None
    
    def buy(self, Q):
        self.quantity += Q

    def sell(self, Q):
        self.quantity -= Q
        if self.quantity < 0:
            self.quantity += Q
            raise server.NegativeAssetException()
        
    def serialize(self, ID):
        id_hex = str(ID).encode("hex")
        q_hex = str(self.quantity).encode("hex")
        serialized_data = id_hex + ";" + q_hex
        return serialized_data
    
    @staticmethod
    def deserialize(serialized_data):
        if serialized_data is None:
            return
        serialized_data = serialized_data.split(";")
        ID = serialized_data[0].decode("hex")
        q = serialized_data[1].decode("hex")
        return FakeAsset(ID, float(q))

    def __eq__(self, other):
        return self.id == other.id and self.quantity == other.quantity
        
class Portfolio(unittest.TestCase):
    def test_init(self):
        user = "john"
        portfolio = server.Portfolio(user)
        self.assertEquals(portfolio.user, user, "User does not match expected result")
        self.assertEquals(portfolio.assets, {}, "Portfolio assets does not match expected result (empty dictionary)")
        self.assertEquals(portfolio.nav, 0, "Portfolio NAV does not match expected result (0)")
        
    def test_eq(self):
        user = "john"
        portfolio1 = server.Portfolio(user)
        portfolio1.assets = {0: FakeAsset(0, 7.5), 1: FakeAsset(1, 11.2)}
        portfolio1.nav = 97.9
        portfolio2 = server.Portfolio(user)
        portfolio2.assets = {0: FakeAsset(0, 7.5), 1: FakeAsset(1, 11.2)}
        portfolio2.nav = 97.9
        self.assertTrue(portfolio1 == portfolio2)
      
    def test_buy_sell_zero(self):
        user = "john"
        asset_id = 1
        Q_before = 11.2
        portfolio = server.Portfolio(user)
        portfolio.assets = {asset_id: FakeAsset(asset_id, Q_before)}
        portfolio.nav = 2.5 * Q_before
        Q = 0
        portfolio.buy_sell(asset_id, Q)
        self.assertEquals(portfolio.user, user)
        self.assertEquals(portfolio.assets[asset_id].quantity, Q_before)
        self.assertEquals(portfolio.nav, 2.5 * Q_before)
    
    def test_buy_asset_not_present(self):
        database = dict()
        database["asset_id_2"] = {"id": 2,"name":"Silver","price":5.0,"class":"metals"}
        server.redis_server = FakeRedisServer(database)
        user = "john"
        portfolio = server.Portfolio(user)
        portfolio.assets = {0: FakeAsset(0,5.0), 1: FakeAsset(1,7.5)}
        nav = 2.5 * 5.0 + 2.5 * 7.5
        portfolio.nav = nav
        asset_id = 2
        Q = 4.0
        portfolio.buy_sell(asset_id, Q)
        self.assertEquals(portfolio.user, user)
        self.assertEquals(portfolio.assets[asset_id].id, asset_id)
        self.assertEquals(portfolio.assets[asset_id].quantity, Q)
        self.assertEquals(portfolio.nav, nav + 5.0 * Q)
        
    def test_sell_asset_not_present(self):
        database = dict()
        database["asset_id_2"] = {"id": 2,"name":"Silver","price":5.0,"class":"metals"}
        server.redis_server = FakeRedisServer(database)
        user = "john"
        assets_before = {0: FakeAsset(0,5.0), 1: FakeAsset(1,5.0)}
        portfolio = server.Portfolio(user)
        portfolio.assets = assets_before
        asset_id = 2
        Q = -2.5
        with self.assertRaises(server.AssetNotFoundException):
            portfolio.buy_sell(asset_id, Q)
        self.assertEquals(portfolio.assets, assets_before)
    
    def test_buy(self):
        user = "john"
        portfolio = server.Portfolio(user)
        asset_id = 1
        portfolio.assets = {asset_id: FakeAsset(asset_id, 5.0)}
        portfolio.nav = 2.5 * 5.0
        Q = 2.5
        portfolio.buy_sell(asset_id, Q)
        self.assertEquals(portfolio.user, user)
        self.assertEquals(portfolio.assets[asset_id], FakeAsset(asset_id, 7.5))
        self.assertEquals(portfolio.nav, portfolio.assets[asset_id].price * 7.5)

    def test_sell(self):
        user = "john"
        portfolio = server.Portfolio(user)
        asset_id = 1
        portfolio.assets = {asset_id: FakeAsset(asset_id, 5.0)}
        portfolio.nav = 2.5 * 5.0
        Q = -2.5
        portfolio.buy_sell(asset_id, Q)
        self.assertEquals(portfolio.user, user)
        self.assertEquals(portfolio.assets[asset_id], FakeAsset(asset_id, 2.5))
        self.assertEquals(portfolio.nav, portfolio.assets[asset_id].price * 2.5)

    def test_sell_zero_result(self):
        user = "john"
        portfolio = server.Portfolio(user)
        asset_id = 1
        portfolio.assets = {asset_id: FakeAsset(asset_id, 5.0)}
        portfolio.nav = 2.5 * 5.0
        Q = -5.0
        portfolio.buy_sell(asset_id, Q)
        self.assertEquals(portfolio.user, user)
        self.assertEquals(portfolio.assets, {})
        self.assertEquals(portfolio.nav, 0)
    
    def test_sell_asset_negative_quantity(self):
        user = "john"
        portfolio = server.Portfolio(user)
        asset_id = 1
        portfolio.assets = {asset_id: FakeAsset(asset_id, 5.0)}
        portfolio.nav = 2.5 * 5.0
        portfolio_expected = portfolio.copy()
        Q = -5.1
        with self.assertRaises(server.NegativeAssetException):
            portfolio.buy_sell(asset_id, Q)
        self.assertEquals(portfolio, portfolio_expected)
    
    def test_remove_asset(self):
        user = "john"
        portfolio = server.Portfolio(user)
        asset_id = 1
        portfolio.assets = {asset_id: FakeAsset(asset_id, 5.0)}
        portfolio.nav = 2.5 * 5.0
        portfolio_expected = portfolio.copy()
        portfolio_expected.nav = 0
        portfolio.remove_asset(asset_id)
        self.assertEquals(portfolio, portfolio_expected)
    
    def test_json_serialize(self):
        user = "john"
        nav = 2.5 * 5.0 + 2.5 * 7.0
        portfolio = server.Portfolio(user)
        portfolio.assets = {0: FakeAsset(0, 5.0), 1: FakeAsset(1, 7.0)}
        portfolio.nav = nav
        url_root = "http://localhost:5000/"
        json_data = portfolio.json_serialize(user, url_root)
        self.assertEquals(json_data, {"user":user, "numberOfAssets":2, "netAssetValue":nav, "links": [{"rel":"self", "href": url_root[:-1]+url_version+"/portfolios/"+user}]})

    def test_serialize(self):
        user = "john"
        portfolio = server.Portfolio(user)
        portfolio.assets = {0: FakeAsset(0, 5.0), 1: FakeAsset(1, 6.0)}
        portfolio.nav = 2.5 * 5.0 + 2.5 * 6.0
        data = portfolio.serialize()
        self.assertEquals(data, "6a6f686e;33303b3335326533302333313b333632653330")
    
    def test_deserialize(self):
        user = "john"
        portfolio_expected = server.Portfolio(user)
        portfolio_expected.assets = {0: FakeAsset(0, 5.0), 1: FakeAsset(1, 6.0)}
        portfolio_expected.nav = 2.5 * 5.0 + 2.5 * 6.0
        data = "6a6f686e;33303b3335326533302333313b333632653330"
        server.Asset = FakeAsset #for the Asset.deserialize method
        portfolio = server.Portfolio.deserialize(data)
        self.assertEquals(portfolio, portfolio_expected)
    
    def test_copy(self):
        user = "john"
        assets = {0: FakeAsset(0,5.0), 1: FakeAsset(1,5.0)}
        nav = 100
        p1 = server.Portfolio(user)
        p1.assets = assets
        p1.nav = nav
        p2 = p1.copy()
        self.assertEquals(p1, p2)
        p2.nav = 50
        self.assertNotEquals(p1, p2)
        
    def test_repr(self):
        no_exception = True
        portfolio = server.Portfolio("john")
        try:
            _ = str(portfolio)
        except:
            no_exception = False
        self.assertTrue(no_exception)
        
class Static(unittest.TestCase):
    def setUp(self):
        self.app = server.app.test_client()
        """ BE WARNED: This checks for local files in static/ """
        
    def test_index(self):
        response = self.app.get("/")
        self.assertNotEquals(response.status_code, HTTP_404_NOT_FOUND)
    
    def test_send_lib(self):
        response = self.app.get("/lib/backbone-min.js")
        self.assertNotEquals(response.status_code, HTTP_404_NOT_FOUND)
    
    def test_send_spec(self):
        response = self.app.get("/specification/portfolioMgmt.js")
        self.assertNotEquals(response.status_code, HTTP_404_NOT_FOUND)
    
    def test_send_img(self):
        response = self.app.get("/images/explorer_icons.png")
        self.assertNotEquals(response.status_code, HTTP_404_NOT_FOUND)
    
    def test_send_css(self):
        response = self.app.get("/css/style.css")
        self.assertNotEquals(response.status_code, HTTP_404_NOT_FOUND)
    
    def test_send_fonts(self):
        response = self.app.get("/fonts/DroidSans.ttf")
        self.assertNotEquals(response.status_code, HTTP_404_NOT_FOUND)

class GET(unittest.TestCase):
    def setUp(self):
        self.app = server.app.test_client()
        
    def test_list_portfolios(self):
        database = dict()
        database["asset_id_0"] = {"id": 0,"name":"gold","price":1286.59,"class":"commodity"}
        database["user_john"] = {"name":"john", "data":"6a6f686e;33303b3335"}
        database["user_jeremy"] = {"name":"jeremy", "data":"6a6572656d79;"}
        database["list_users"] = set(["john", "jeremy"])
        server.redis_server = FakeRedisServer(database)
        response = self.app.get(url_version+"/portfolios")
        parsed_data = json.loads(response.data)
        self.assertEquals(response.status_code, HTTP_200_OK)
        self.assertEquals(parsed_data["portfolios"][0]["user"], "john")
        self.assertEquals(parsed_data["portfolios"][1]["user"], "jeremy")
        self.assertEquals(parsed_data["portfolios"][0]["numberOfAssets"], 1)
        self.assertEquals(parsed_data["portfolios"][1]["numberOfAssets"], 0)
        self.assertEquals(parsed_data["portfolios"][0]["netAssetValue"], 6432.95)
        self.assertEquals(parsed_data["portfolios"][1]["netAssetValue"], 0)
        self.assertEquals(parsed_data["portfolios"][0]["links"][0]["rel"], "self")
        self.assertEquals(parsed_data["portfolios"][1]["links"][0]["rel"], "self")
        self.assertEquals(parsed_data["portfolios"][0]["links"][0]["href"], "http://localhost"+url_version+"/portfolios/john")
        self.assertEquals(parsed_data["portfolios"][1]["links"][0]["href"], "http://localhost"+url_version+"/portfolios/jeremy")
    
    def test_list_assets(self):
        database = dict()
        database["asset_id_0"] = {"id": 0,"name":"gold","price":1286.59,"class":"commodity"}
        database["user_john"] = {"name":"john", "data":"6a6f686e;33303b3335"}
        server.redis_server = FakeRedisServer(database)
        response = self.app.get(url_version+"/portfolios/john/assets")
        parsed_data = json.loads(response.data)
        self.assertEquals(response.status_code, HTTP_200_OK)
        self.assertEquals(parsed_data["assets"][0]["id"], 0)
        self.assertEquals(parsed_data["assets"][0]["name"], "gold")
    
    def test_list_assets_no_username(self):
        database = dict()
        database["asset_id_0"] = {"id": 0,"name":"gold","price":1286.59,"class":"commodity"}
        server.redis_server = FakeRedisServer(database)
        response = self.app.get(url_version+"/portfolios/john/assets")
        parsed_data = json.loads(response.data)
        self.assertEquals(parsed_data["error"], "User john not found")
        self.assertEquals(response.status_code, HTTP_404_NOT_FOUND)
    
    def test_get_asset(self):
        database = dict()
        database["asset_id_0"] = {"id": 0,"name":"gold","price":1286.59,"class":"commodity"}
        database["user_john"] = {"name":"john", "data":"6a6f686e;33303b3335"}
        server.redis_server = FakeRedisServer(database)
        response = self.app.get(url_version+"/portfolios/john/assets/0")
        parsed_data = json.loads(response.data)
        self.assertEquals(parsed_data["name"], "gold")
        self.assertEquals(parsed_data["quantity"], 5.0)
        self.assertEquals(parsed_data["value"], 5.0*1286.59)
        self.assertEquals(response.status_code, HTTP_200_OK)
    
    def test_get_asset_no_username(self):
        database = dict()
        database["asset_id_0"] = {"id": 0,"name":"gold","price":1286.59,"class":"commodity"}
        server.redis_server = FakeRedisServer(database)
        response = self.app.get(url_version+"/portfolios/john/assets/0")
        parsed_data = json.loads(response.data)
        self.assertEquals(parsed_data["error"], "User john not found")
        self.assertEquals(response.status_code, HTTP_404_NOT_FOUND)
    
    def test_get_asset_no_data(self):
        database = dict()
        database["asset_id_0"] = {"id": 0,"name":"gold","price":1286.59,"class":"commodity"}
        database["user_john"] = {"name":"john", "data":""}
        server.redis_server = FakeRedisServer(database)
        response = self.app.get(url_version+"/portfolios/john/assets/0")
        parsed_data = json.loads(response.data)
        self.assertEquals(parsed_data["error"],"The portfolio of user john has no data!") 
        self.assertEquals(response.status_code, HTTP_404_NOT_FOUND)
    
    def test_get_asset_no_assetid(self):
        database = dict()
        database["asset_id_0"] = {"id": 0,"name":"gold","price":1286.59,"class":"commodity"}
        database["user_john"] = {"name":"john", "data":"6a6f686e;"}
        server.redis_server = FakeRedisServer(database)
        response = self.app.get(url_version+"/portfolios/john/assets/0")
        parsed_data = json.loads(response.data)
        self.assertEquals(parsed_data["error"], "Asset with id 0 does not exist in this portfolio")
        self.assertEquals(response.status_code, HTTP_404_NOT_FOUND)
    
    def test_get_nav(self):
        database = dict()
        database["asset_id_0"] = {"id": 0,"name":"gold","price":1286.59,"class":"commodity"}
        database["user_john"] = {"name":"john", "data":"6a6f686e;33303b3335"}
        server.redis_server = FakeRedisServer(database)
        response = self.app.get(url_version+"/portfolios/john/nav")
        parsed_data = json.loads(response.data)
        self.assertEquals(parsed_data["nav"], 6432.95)
        self.assertEquals(response.status_code, HTTP_200_OK)
    
    def test_get_nav_no_username(self):
        database = dict()
        database["asset_id_0"] = {"id": 0,"name":"gold","price":1286.59,"class":"commodity"}
        server.redis_server = FakeRedisServer(database)
        response = self.app.get(url_version+"/portfolios/john/nav")
        parsed_data = json.loads(response.data)
        self.assertEquals(parsed_data["error"], "User john not found")
        self.assertEquals(response.status_code, HTTP_404_NOT_FOUND)
    
class POST(unittest.TestCase):
    def setUp(self):
        self.app = server.app.test_client()
    
    def test_create_user(self):
        database = dict()
        server.redis_server = FakeRedisServer(database)
        response = self.app.post(url_version+"/portfolios", data='{"user":"john"}')
        self.assertEquals(response.data, '""\n')
        self.assertEquals(response.status_code, HTTP_201_CREATED)
    
    def test_create_user_data_not_valid(self):
        response = self.app.post(url_version+"/portfolios", data='notjson')
        parsed_data = json.loads(response.data)
        self.assertEquals(parsed_data["error"], "Data notjson is not valid")
        self.assertEquals(response.status_code, HTTP_400_BAD_REQUEST)
    
    def test_create_user_payload_not_valid(self):
        response = self.app.post(url_version+"/portfolios", data='{"wrong_key":"john"}')
        parsed_data = json.loads(response.data)
        self.assertEquals(parsed_data["error"], "Payload {u'wrong_key': u'john'} is not valid")
        self.assertEquals(response.status_code, HTTP_400_BAD_REQUEST)
    
    def test_create_user_already_exists(self):
        database = dict()
        database["user_john"] = {"name":"john", "data":"6a6f686e;33303b3335"}
        server.redis_server = FakeRedisServer(database)
        response = self.app.post(url_version+"/portfolios", data='{"user":"john"}')
        self.assertEquals(response.status_code, HTTP_409_CONFLICT)
        parsed_data = json.loads(response.data)
        self.assertEquals(parsed_data["error"], "User john already exists")
    
    def test_create_asset(self):
        database = dict()
        database["user_john"] = {"name":"john", "data":"6a6f686e;33303b3335"}
        database["asset_id_0"] = {"id": 0,"name":"gold","price":1286.59,"class":"commodity"}
        database["asset_id_1"] = {"id": 1,"name":"NYC real estate index","price":16255.18,"class":"real-estate"}
        server.redis_server = FakeRedisServer(database)
        response = self.app.post(url_version+"/portfolios/john/assets", data='{"asset_id":1,"quantity":10}')
        self.assertEquals(response.data, '""\n')
        self.assertEquals(response.status_code, HTTP_201_CREATED)
    
    def test_create_asset_neg(self):
        database = dict()
        database["user_john"] = {"name":"john", "data":"6a6f686e;33303b3335"}
        database["asset_id_0"] = {"id": 0,"name":"gold","price":1286.59,"class":"commodity"}
        database["asset_id_1"] = {"id": 1,"name":"NYC real estate index","price":16255.18,"class":"real-estate"}
        server.redis_server = FakeRedisServer(database)
        response = self.app.post(url_version+"/portfolios/john/assets", data='{"asset_id":1,"quantity":-10}')
        parsed_data = json.loads(response.data)
        self.assertEquals(parsed_data["error"], "Quantity value must be positive")
        self.assertEquals(response.status_code, HTTP_400_BAD_REQUEST)
    
    def test_create_asset_data_not_valid(self):
        response = self.app.post(url_version+"/portfolios/john/assets", data='notjson')
        parsed_data = json.loads(response.data)
        self.assertEquals(parsed_data["error"], "Data notjson is not valid")
        self.assertEquals(response.status_code, HTTP_400_BAD_REQUEST)
    
    def test_create_asset_payload_not_valid(self):
        response = self.app.post(url_version+"/portfolios/john/assets", data='{"wrong_key":"john"}')
        parsed_data = json.loads(response.data)
        self.assertEquals(parsed_data["error"], "Payload {u'wrong_key': u'john'} is not valid")
        self.assertEquals(response.status_code, HTTP_400_BAD_REQUEST)
    
    def test_create_asset_no_assetid(self):
        database = dict()
        database["user_john"] = {"name":"john", "data":"6a6f686e;33303b3335"}
        database["asset_id_0"] = {"id": 0,"name":"gold","price":1286.59,"class":"commodity"}
        server.redis_server = FakeRedisServer(database)
        response = self.app.post(url_version+"/portfolios/john/assets", data='{"asset_id":1,"quantity":10}')
        parsed_data = json.loads(response.data)
        self.assertEquals(parsed_data["error"], "Asset id 1 does not exist in database")
        self.assertEquals(response.status_code, HTTP_400_BAD_REQUEST)
    
    def test_create_asset_no_username(self):
        database = dict()
        database["asset_id_0"] = {"id": 0,"name":"gold","price":1286.59,"class":"commodity"}
        database["asset_id_1"] = {"id": 1,"name":"NYC real estate index","price":16255.18,"class":"real-estate"}
        server.redis_server = FakeRedisServer(database)
        response = self.app.post(url_version+"/portfolios/john/assets", data='{"asset_id":1,"quantity":10}')
        parsed_data = json.loads(response.data)
        self.assertEquals(parsed_data["error"], "User john not found")
        self.assertEquals(response.status_code, HTTP_404_NOT_FOUND)
    
    def test_create_asset_already_exists(self):
        database = dict()
        database["user_john"] = {"name":"john", "data":"6a6f686e;33303b3335"}
        database["asset_id_0"] = {"id": 0,"name":"gold","price":1286.59,"class":"commodity"}
        server.redis_server = FakeRedisServer(database)
        response = self.app.post(url_version+"/portfolios/john/assets", data='{"asset_id":0,"quantity":10}')
        parsed_data = json.loads(response.data)
        self.assertEquals(parsed_data["error"], "Asset with id 0 already exists in portfolio.")
        self.assertEquals(response.status_code, HTTP_409_CONFLICT)
    
class PUT(unittest.TestCase):
    def setUp(self):
        self.app = server.app.test_client()
        
    def test_update_asset(self):
        database = dict()
        database["user_john"] = {"name":"john", "data":"6a6f686e;33303b3335"}
        database["asset_id_0"] = {"id": 0,"name":"gold","price":1286.59,"class":"commodity"}
        server.redis_server = FakeRedisServer(database)
        response = self.app.put(url_version+"/portfolios/john/assets/0", data='{"quantity":10}')
        self.assertEquals(response.data, '""\n')
        self.assertEquals(response.status_code, HTTP_200_OK)
    
    def test_update_asset_data_not_valid(self):
        response = self.app.put(url_version+"/portfolios/john/assets/0", data='notjson')
        parsed_data = json.loads(response.data)
        self.assertEquals(parsed_data["error"], "Data notjson is not valid")
        self.assertEquals(response.status_code, HTTP_400_BAD_REQUEST)

    
    def test_update_asset_payload_not_valid(self):
        response = self.app.put(url_version+"/portfolios/john/assets/0", data='{"wrong_key":10}')
        parsed_data = json.loads(response.data)
        self.assertEquals(parsed_data["error"], "Payload {u'wrong_key': 10} is not valid")
        self.assertEquals(response.status_code, HTTP_400_BAD_REQUEST)
    
    def test_update_asset_assetid_not_integer(self):
        response = self.app.put(url_version+"/portfolios/john/assets/string", data='{"quantity":10}')
        parsed_data = json.loads(response.data)
        self.assertEquals(parsed_data["error"], "The asset_id string is not an integer")
        self.assertEquals(response.status_code, HTTP_400_BAD_REQUEST)
    
    def test_update_asset_no_username(self):
        database = dict()
        database["asset_id_0"] = {"id": 0,"name":"gold","price":1286.59,"class":"commodity"}
        server.redis_server = FakeRedisServer(database)
        response = self.app.put(url_version+"/portfolios/john/assets/0", data='{"quantity":10}')
        parsed_data = json.loads(response.data)
        self.assertEquals(parsed_data["error"], "User john not found")
        self.assertEquals(response.status_code, HTTP_404_NOT_FOUND)
    
    def test_update_asset_no_data(self):
        database = dict()
        database["user_john"] = {"name":"john", "data":""}
        database["asset_id_0"] = {"id": 0,"name":"gold","price":1286.59,"class":"commodity"}
        server.redis_server = FakeRedisServer(database)
        response = self.app.put(url_version+"/portfolios/john/assets/0", data='{"quantity":10}')
        parsed_data = json.loads(response.data)
        self.assertEquals(parsed_data["error"], "No data associated with user john")
        self.assertEquals(response.status_code, HTTP_404_NOT_FOUND)
    
    def test_update_asset_asset_not_found(self):
        database = dict()
        database["user_john"] = {"name":"john", "data":"6a6f686e;33303b3335"}
        database["asset_id_0"] = {"id": 0,"name":"gold","price":1286.59,"class":"commodity"}
        database["asset_id_1"] = {"id": 1,"name":"NYC real estate index","price":16255.18,"class":"real-estate"}
        server.redis_server = FakeRedisServer(database)
        response = self.app.put(url_version+"/portfolios/john/assets/1", data='{"quantity":10}')
        parsed_data = json.loads(response.data)
        self.assertEquals(parsed_data["error"], "Asset with id 1 was not found in the portfolio of john.")
        self.assertEquals(response.status_code, HTTP_404_NOT_FOUND)
    
    def test_update_asset_negative(self):
        database = dict()
        database["user_john"] = {"name":"john", "data":"6a6f686e;33303b3335"}
        database["asset_id_0"] = {"id": 0,"name":"gold","price":1286.59,"class":"commodity"}
        server.redis_server = FakeRedisServer(database)
        response = self.app.put(url_version+"/portfolios/john/assets/0", data='{"quantity":-20.7}')
        parsed_data = json.loads(response.data)
        self.assertEquals(parsed_data["error"], "Selling 20 units of the asset with id 0 in the portfolio of john would result in a negative quantity. The operation was aborted.")
        self.assertEquals(response.status_code, HTTP_400_BAD_REQUEST)
    
class DELETE(unittest.TestCase):
    def setUp(self):
        self.app = server.app.test_client()

    def test_delete_asset(self):
        database = dict()
        database["user_john"] = {"name":"john", "data":"6a6f686e;33303b3335"}
        database["asset_id_0"] = {"id": 0,"name":"gold","price":1286.59,"class":"commodity"}
        server.redis_server = FakeRedisServer(database)
        response = self.app.delete(url_version+"/portfolios/john/assets/0")
        self.assertEquals(response.data, '')
        self.assertEquals(response.status_code, HTTP_204_NO_CONTENT)
    
    def test_delete_user(self):
        database = dict()
        database["user_john"] = {"name":"john", "data":"6a6f686e;33303b3335"}
        database["asset_id_0"] = {"id": 0,"name":"gold","price":1286.59,"class":"commodity"}
        database["list_users"] = set()
        database["list_users"].add("john")
        server.redis_server = FakeRedisServer(database)
        response = self.app.delete(url_version+"/portfolios/john")
        self.assertEquals(response.data, '')
        self.assertEquals(response.status_code, HTTP_204_NO_CONTENT)
    
class Utility(unittest.TestCase):
    def setUp(self):
        self.app = server.app.test_client()
    
    def test_reply(self):
        message = "message message message"
        rc = 404
        #response = server.reply(message, rc)
        #self.assertEquals(response, "") XXX
    
    def test_is_valid_true(self):
        data = {"key1":2312, "key2":434}
        valid = server.is_valid(data, ["key1", "key2"])
        self.assertTrue(valid)
    
    def test_is_valid_false(self):
        data = {"key1":2312}
        valid = server.is_valid(data, ["key2"])
        self.assertFalse(valid)
        
    def test_init_redis_connection(self):
        server.redis_server = FakeRedisServer()
        with self.assertRaises(server.RedisConnectionException):
            server.init_redis("localhost:5000", 5000, None)
            
class Credentials(unittest.TestCase):
    def test_init(self):
        no_exception = True
        try:
            _ = server.Credentials("linux", "localhost:5000", 5000, "password", "localhost")
        except:
            no_exception = False
        self.assertTrue(no_exception)
        
    def test_eq(self):
        creds = server.Credentials("linux", "localhost:5000", 5000, "abc", "swagger")
        self.assertTrue(creds.environment == "linux" and creds.host == "localhost:5000" and creds.port == 5000 and creds.password == "abc" and creds.swagger_host == "swagger")
        
class FakePath(object):
    def __init__(self, docker=False):
        self.docker = docker
    
    def isfile(self, filename):
        return self.docker
    
class FakeOS(object):
    def __init__(self, bluemix=False, docker=False):
        self.environ = dict()
        self.path = FakePath(docker)
        if bluemix:
            data = json.dumps({"rediscloud":[{"credentials":{"hostname":"0.0.0.0","port":"6000","password":"abcde"}}]})
            self.environ["VCAP_SERVICES"] = data
            
class Other(unittest.TestCase):
    def test_determine_credentials_bluemix(self):
        server.os = FakeOS(True, False)
        creds_expected = server.Credentials("Bluemix", "0.0.0.0", 6000, "abcde", "portfoliomgmt.mybluemix.net")
        creds = server.determine_credentials()
        self.assertEquals(creds, creds_expected)
        
    def test_determine_credentials_bluemix_container(self):
        server.os = FakeOS(True, True)
        creds_expected = server.Credentials("Docker running in Bluemix", "0.0.0.0", 6000, "abcde", "portfoliocontainer.mybluemix.net")
        creds = server.determine_credentials()
        self.assertEquals(creds, creds_expected)
        
    def test_determine_credentials_vagrant(self):
        server.os = FakeOS(False, False)
        creds_expected = server.Credentials("Vagrant", "127.0.0.1", 6379, None, "localhost:5000")
        creds = server.determine_credentials()
        self.assertEquals(creds, creds_expected)
        
    def test_determine_credentials_vagrant_container(self):
        server.os = FakeOS(False, True)
        creds_expected = server.Credentials("Docker running in Vagrant", "redis", 6379, None, "localhost:5000")
        creds = server.determine_credentials()
        self.assertEquals(creds, creds_expected)
        
    def test_fill_database_assets(self):
        server.redis_server = FakeRedisServer(dict())
        exception_raised = False
        try:
            server.fill_database_assets()
        except:
            exception_raised = True
        self.assertFalse(exception_raised)
        
        

######################################################################
#   M A I N
######################################################################
if __name__ == "__main__":
    unittest.main()
