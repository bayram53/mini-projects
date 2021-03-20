#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Sun Mar 14 03:00:45 2021

@author: bayram
"""


import unittest;
import sys;
import numpy as np;
import pdb;
#from bson import ObjectId
sys.path.append('../main');

from Block import Block;
from database import Connect;

class TestBlock(unittest.TestCase):
    def test_add_user(self):
        db = Connect().get_db();
        oid = db['blocks'].insert_one({}).inserted_id
        block = Block(oid, db);

        n = 100;
        ids = [];
        points = [];
        
        for i in range(n):
            ids.append(i);
            points.append((i**2) % 23);
            block.add_user(str(ids[i]), int(points[i]));
        
        ids = list(map(str, ids));
        tmp = list(zip(points, ids));
        tmp = sorted(tmp, reverse=True);
        
        t_points, t_ids = list(zip(*tmp));
        t_vals = (list(t_ids), list(t_points));
        
        tmp = block.get_users();
        p_ids = [e['id'] for e in tmp]
        p_points = [e['points'] for e in tmp]
        p_vals = (p_ids, p_points);
        
        #pdb.set_trace();
        
        self.assertEqual(t_vals, p_vals);
    
    def test_delete(self):
        db = Connect().get_db();
        oid = db['blocks'].insert_one({}).inserted_id
        block = Block(oid, db);
        
        n = 100;
        ids = [];
        points = [];
        
        for i in range(n):
            ids.append(i);
            points.append((i**2) % 23);
            block.add_user(str(ids[i]), int(points[i]));
        ids = list(map(str, ids));
        
        for i in range(n):
            if len(ids) <= i: break;
            if np.random.uniform() < 0.2:
                uid = ids[i];
                ids.pop(i);
                points.pop(i);
                block.delete_user(uid);                
        
        tmp = list(zip(points, ids));
        tmp = sorted(tmp, reverse=True);
        
        t_points, t_ids = list(zip(*tmp));
        t_vals = (list(t_ids), list(t_points));
        
        tmp = block.get_users();
        p_ids = [e['id'] for e in tmp]
        p_points = [e['points'] for e in tmp]
        p_vals = (p_ids, p_points);
        
        self.assertEqual(t_vals, p_vals);

    
    def test_divide(self):
        db = Connect().get_db();
        oid = db['blocks'].insert_one({}).inserted_id
        block = Block(oid, db);

        n = 53;
        
        block_size = 13;
        
        ids = np.random.randint(low=0, high=10000, size=n);
        points = np.random.randint(low=0, high=10000, size=n);
        
        for i in range(n):
            block.add_user(str(ids[i]), int(points[i]));
        
        new_ids = block.divide(block_size);
        new_ids = [oid] + new_ids;
        
        ids = list(map(str, ids));
        tmp = list(zip(points, ids));
        tmp = sorted(tmp, reverse=True);
        points, ids = list(zip(*tmp));
        points, ids = list(points), list(ids);
        
        t_vals = [];
        p_vals = [];
        for i in range(n//block_size+1):
            l = i*block_size;
            r = min((i+1)*block_size, n);
            
            t_vals.append((ids[l:r], points[l:r]));
            
            b = Block(new_ids[i], db);
            tmp = b.get_users();
            p_ids = [e['id'] for e in tmp]
            p_points = [e['points'] for e in tmp]
            p_vals.append((p_ids, p_points));
        
        self.assertEqual(t_vals, p_vals);
    
    def test_combine(self):
        db = Connect().get_db();
        
        blocks = [];
        all_ids = [];
        all_points = [];
        
        
        n = 7;
        for i in range(n):
            blocks.append(db['blocks'].insert_one({}).inserted_id);
        
        for j in range(n):
            n_each = np.random.randint(10,15);
            
            ids = np.random.randint(low=0, high=10000, size=n_each);
            points = np.random.randint(low=0, high=10000, size=n_each);
            
            block = Block(blocks[j], db);
            for i in range(n_each):
                block.add_user(str(ids[i]), int(points[i]));
            
            all_ids += list(ids);
            all_points += list(points);
        
        all_ids = list(map(str, all_ids));    
        tmp = list(zip(all_points, all_ids));
        tmp = sorted(tmp, reverse=True);
        points, ids = list(zip(*tmp));
        points, ids = list(points), list(ids);
        
        b = Block(blocks[0], db);
        for i in range(1, len(blocks)):
            Block(blocks[i], db).combine(blocks[0]);
        
        t_vals = (ids, points);
        
        tmp = b.get_users();
        p_ids = [e['id'] for e in tmp]
        p_points = [e['points'] for e in tmp]
        p_vals = (p_ids, p_points);
        
        self.assertEqual(t_vals, p_vals);
    
    

if __name__ == '__main__':
    unittest.main();
