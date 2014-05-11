# -*- coding: UTF-8 -*-

from define import *
import pymongo


###################################################################
######################### User Handlers ###########################
###################################################################
class DB():
    DataBase = None
    Table = None

    def __init__(self, database=None):
        self.DataBase = None
        self.Table = None

        if IS_BAE == True:
            conn = pymongo.Connection(host = "mongo.duapp.com", port = 8908)  
            database = "AXuAgnJLApkefuWllnSG"
            self.DataBase = conn[database]
            api_key = "IXj5gFpzufduRv3BnG9i255H"
            secret_key = "yFmYQhLyItkE6i54CPRXBiQKkcOZa1UP"
            self.DataBase.authenticate(api_key, secret_key)
        else:
            #conn = pymongo.Connection("117.121.241.216", 27017)
            conn = pymongo.Connection("127.0.0.1", 27017)
            if database != None:
                self.DataBase = conn[database]
            else:
                log_print('db init faled: identify the db name')

    def SelectTable(self, table): # table is the same as collection
        self.Table = table
        return self.DataBase[table]

    def FindOne(self, key, val):
        return self.DataBase[self.Table].find_one({key: val})

    def Find(self):
        return self.DataBase[self.Table].find()

    def Update(self, entry):
        return self.DataBase[self.Table].save(entry)

    def Insert(self, entry):
        return self.DataBase[self.Table].insert(entry)

    def Count(self):
        return self.DataBase[self.Table].count()


###################################################################
######################## Test Handlers ############################
###################################################################


