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
    pass
        
        


######################################################################
#   M A I N
######################################################################
if __name__ == "__main__":
    unittest.main()
