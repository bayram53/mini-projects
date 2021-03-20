#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Sun Mar 14 00:32:19 2021

@author: bayram
"""


from pymongo import MongoClient;

class Connect(object):
    def __init__(self):
        f = open('./db_info.txt', 'r')
        db_password = f.readline().strip();
        f.close();
        #self.client = MongoClient("mongodb+srv://user1:"+db_password+"@cluster0.spz5z.mongodb.net/myFirstDatabase?retryWrites=true&w=majority")
        self.client = MongoClient();
        
    def get_db_names(self):
        return self.client.list_database_names();
    
    def have_db(self, db_name):
        return db_name in self.get_db_names();
    
    def get_db(self, db_name='deneme_database'):
        return self.client[db_name];

"""
client = Connect.get_connection();
db = client['deneme_database'];

db["deneme_collection"].insert_one(
    {"item": "canvas",
     "qty": 100,
     "tags": ["cotton"],
     "size": {"h": 28, "w": 35.5, "uom": "cm"}});
"""

if __name__ == '__main__':
    c = Connect();
    for db_name in c.get_db_names():
        if db_name == 'admin' or db_name == 'local': continue;
        c.client.drop_database(db_name)
