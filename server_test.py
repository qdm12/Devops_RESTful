import unittest
import server

# Status Codes
HTTP_200_OK = 200
HTTP_201_CREATED = 201
HTTP_204_NO_CONTENT = 204
HTTP_400_BAD_REQUEST = 400
HTTP_404_NOT_FOUND = 404
HTTP_409_CONFLICT = 409

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
        if self.database is None:
            database = dict()
            database["asset_id_0"] = {"id": 0,"name":"gold","price":1286.59,"class":"commodity"}
            database["asset_id_1"] = {"id": 1,"name":"NYC real estate index","price":16255.18,"class":"real-estate"}
            database["asset_id_2"] = {"id": 2,"name":"brent crude oil","price":51.45,"class":"commodity"}
            database["asset_id_3"] = {"id": 3,"name":"US 10Y T-Note","price":130.77,"class":"fixed income"}
            database["user_john"] = {"name":"john", "data":"6a6f686e;33303b3335"}
            database["user_jeremy"] = {"name":"jeremy", "data":""}
            database["list_users"] = set(["john", "jeremy"])
        
    def hget(self, key, field):
        """
        * key "asset_id_2" and field "id"/"name"/"price"/"class"
            or
        * key "user_john" and field "name"/"data"
        """
        return self.database[key][field]
    
    def hmset(self, key, dictionary):
        for subkey in dictionary:
            self.database[key][subkey] = dictionary[subkey]
            
    def hdel(self, key, dictionary):
        for subkey in dictionary:
            del self.database[key][subkey]
    
    def smembers(self, key="list_users"):
        return self.database[key]
    
    def sadd(self, key="list_users", user="john"):
        self.database[key].add(user)
    
    def srem(self, key="list_users", user="john"):
        self.database[key].remove(user)
        
    def delete(self, key):
        del self.database[key]
        

class NegativeAssetException(unittest.TestCase):
    def test_exception(self):
        exception_raised = False
        try:
            raise server.NegativeAssetException()
        except:
            exception_raised = True
        self.assertEquals(exception_raised, True, "NegativeAssetException was not raised")
        
class AssetNotFoundException(unittest.TestCase):
    def test_exception(self):
        exception_raised = False
        try:
            raise server.AssetNotFoundException()
        except:
            exception_raised = True
        self.assertEquals(exception_raised, True, "AssetNotFoundException was not raised")
        
class Asset(unittest.TestCase):
    database = dict()
    database["asset_id_1"] = {"id": 1,"name":"NYC real estate index","price":16255.18,"class":"real-estate"}
    server.redis_server = FakeRedisServer(database)    
    
    def test_init(self):
        ID = "1"
        Q = 5
        asset = server.Asset(ID, Q)
        self.assertEquals(asset.id, 1, "Asset id does not match expected result")
        self.assertEquals(asset.asset_class, "real-estate", "Asset class does not match expected result")
        self.assertEquals(asset.name, "NYC real estate index", "Asset name does not match expected result")
        self.assertEquals(asset.price, 16255.18, "Asset price does not match expected result")
        self.assertEquals(asset.quantity, 5, "Asset quantity does not match expected result")
        self.assertEquals(asset.nav, 81275.9, "Asset net value does not match expected result")
        
    def test_init_zero_quantity(self):
        ID = "1"
        Q = 0
        exception_raised = False
        try:
            _ = server.Asset(ID, Q)
        except:
            exception_raised = True
        self.assertEquals(exception_raised, True, "Exception was not raised for zero quantity")
        
    def test_init_neg_quantity(self):
        ID = "1"
        Q = 0
        exception_raised = False
        try:
            _ = server.Asset(ID, Q)
        except:
            exception_raised = True
        self.assertEquals(exception_raised, True, "Exception was not raised for negative quantity")
        
    def test_buy(self):
        ID = "1"
        Q = 5.5
        asset = server.Asset(ID, Q)
        asset.buy(17)
        self.assertEquals(asset.quantity, 22.5, "Asset new quantity does not match expected result")
        self.assertEquals(asset.nav, 365741.55, "Asset net value does not match expected result")
        
    def test_sell(self):
        ID = "1"
        Q = 5.5
        asset = server.Asset(ID, Q)
        asset.sell(1.25)
        self.assertEquals(asset.quantity, 4.25, "Asset new quantity does not match expected result")
        self.assertEquals(asset.nav, 69084.515, "Asset net value does not match expected result")
        
    def test_serialize(self):
        ID = "1"
        Q = 5.5
        asset = server.Asset(ID, Q)
        data = asset.serialize(ID)
        self.assertEquals(data, "31;352e35", "Serialized data does not match expected result")
        
    def test_deserialize(self):
        data = "31;352e35"
        asset = server.Asset.deserialize(data)
        self.assertEquals(asset.id, 1, "Asset id does not match expected result")
        self.assertEquals(asset.asset_class, "real-estate", "Asset class does not match expected result")
        self.assertEquals(asset.name, "NYC real estate index", "Asset name does not match expected result")
        self.assertEquals(asset.price, 16255.18, "Asset price does not match expected result")
        self.assertEquals(asset.quantity, 5.5, "Asset quantity does not match expected result")
        self.assertEquals(asset.nav, 89403.49, "Asset net value does not match expected result")
        
class Portfolio(unittest.TestCase):
    class FakeAsset(object):
        def __init__(self, ID, Q):
            self.quantity = Q
            pass
        
        def buy(self, Q):
            pass

        def sell(self, Q):
            pass        
        
    assets = {0: FakeAsset(0,10), 1: FakeAsset(1,10)}
    
    def test_init(self):
        user = "john"
        portfolio = server.Portfolio(user)
        self.assertEquals(portfolio.user, user, "Asset price does not match expected result")
        self.assertEquals(portfolio.assets, {}, "Portfolio assets does not match expected result (empty dictionary)")
        self.assertEquals(portfolio.nav, 0, "Portfolio NAV does not match expected result (0)")    
      
    def test_buy_zero(self):
        pass
    
    def test_buy_asset_present(self):
        pass
    
    def test_buy_asset_not_present(self):
        pass
    
    def test_sell_zero(self):
        pass
    
    def test_sell_asset_present(self):
        pass
    
    def test_sell_asset_not_present(self):
        pass
    
    def test_sell_asset_negative_quantity(self):
        pass
    
    def test_buy_sell_negative(self):
        pass
    
    def test_buy_sell_positive(self):
        pass
    
    def test_remove_asset_present(self):
        pass
    
    def test_remove_asset_not_present(self):
        pass
    
    def test_json_serialize(self):
        pass
    
    def test_serialize(self):
        pass
    
    def test_deserialize(self):
        pass
    
    def test_deserialize_None(self):
        pass
    
class Static(unittest.TestCase):
    def test_index(self):
        pass
    
    def test_send_js(self):
        pass
    
    def test_send_spec(self):
        pass
    
    def test_send_img(self):
        pass
    
    def test_send_css(self):
        pass
    
    def test_send_fonts(self):
        pass
    
class GET(unittest.TestCase):
    def test_list_portfolios(self):
        pass
    
    def test_list_assets(self):
        pass
    
    def test_list_assets_no_username(self):
        pass
    
    def test_get_asset(self):
        pass
    
    def test_get_asset_no_username(self):
        pass
    
    def test_get_asset_no_data(self):
        pass
    
    def test_get_asset_no_assetid(self):
        pass
    
    def test_get_nav(self):
        pass
    
    def test_get_nav_no_username(self):
        pass
    
class POST(unittest.TestCase):
    def test_create_user(self):
        pass
    
    def test_create_user_data_not_valid(self):
        pass
    
    def test_create_user_payload_not_valid(self):
        pass
    
    def test_create_user_no_username(self):
        pass
    
    def test_create_asset(self):
        pass
    
    def test_create_asset_data_not_valid(self):
        pass
    
    def test_create_asset_payload_not_valid(self):
        pass
    
    def test_create_asset_no_assetid(self):
        pass
    
    def test_create_asset_no_username(self):
        pass
    
    def test_create_asset_already_exists(self):
        pass
    
class PUT(unittest.TestCase):
    def test_update_asset(self):
        pass
    
    def test_update_asset_data_not_valid(self):
        pass
    
    def test_update_asset_payload_not_valid(self):
        pass
    
    def test_update_asset_assetid_not_integer(self):
        pass
    
    def test_update_asset_no_username(self):
        pass
    
    def test_update_asset_no_data(self):
        pass
    
    def test_update_asset_asset_not_found(self):
        pass
    
    def test_update_asset_negative(self):
        pass
    
class DELETE(unittest.TestCase):
    def test_delete_asset(self):
        pass
    
    def test_delete_user(self):
        pass
    
class Utility(unittest.TestCase):
    def test_reply(self):
        pass
    
    def test_is_valid_true(self):
        pass
    
    def test_is_valid_false(self):
        pass
    
            


######################################################################
#   M A I N
######################################################################
if __name__ == "__main__":
    unittest.main()
