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
    def __init__(self, database):
        """ database is a dict of a dict:
        * key 'asset_id_0' and value {"id": 0,"name":"gold","value":1286.59,"type":"commodity"}
            or
        * key 'user_john' and value {"name": "john","data":"6a6f686e;33303b3335"}
            or
        * key 'list_users' and value set("john", ...)
        """
        self.database = database
        if self.database is None:
            database = dict()
            database["asset_id_0"] = {"id": 0,"name":"gold","value":1286.59,"type":"commodity"}
            database["asset_id_1"] = {"id": 1,"name":"NYC real estate index","value":16255.18,"type":"real-estate"}
            database["asset_id_2"] = {"id": 2,"name":"brent crude oil","value":51.45,"type":"commodity"}
            database["asset_id_3"] = {"id": 3,"name":"US 10Y T-Note","value":130.77,"type":"fixed income"}
            database["user_john"] = {"name":"john", "data":"6a6f686e;33303b3335"}
            database["user_jeremy"] = {"name":"jeremy", "data":""}
            database["list_users"] = set(["john", "jeremy"])
        
    def hget(self, key, field):
        """
        * key "asset_id_2" and field "id"/"name"/"value"/"type"
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
        self.assertEquals(exception_raised, True)
        
class AssetNotFoundException(unittest.TestCase):
    def test_exception(self):
        exception_raised = False
        try:
            raise server.AssetNotFoundException()
        except:
            exception_raised = True
        self.assertEquals(exception_raised, True)


######################################################################
#   M A I N
######################################################################
if __name__ == "__main__":
    unittest.main()
