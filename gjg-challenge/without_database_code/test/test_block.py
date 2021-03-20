import unittest;
import sys;
import numpy as np;
sys.path.append('../main');

from Block import Block;

class TestBlock(unittest.TestCase):
    def test_add_user(self):
        block = Block();

        n = 53;
        ids = np.random.randint(low=0, high=10000, size=n);
        points = np.random.randint(low=0, high=10000, size=n);
        
        for i in range(n):
            block.add_user(ids[i], points[i]);
        
        tmp = list(zip(points, ids));
        tmp = sorted(tmp, reverse=True);
        points, ids = list(zip(*tmp));
        
        known_vals = (list(ids), list(points));
        test_vals = (block.user_ids, block.user_points);
        
        self.assertEqual(known_vals, test_vals);
    
    def test_divide(self):
        n = 1234;
        block_size = 100;
        
        ids = np.random.randint(low=0, high=10000, size=n);
        points = np.random.randint(low=0, high=10000, size=n);
        
        block = Block();
        for i in range(n):
            block.add_user(ids[i], points[i]);
        
        new_blocks = block.divide(block_size);
        new_blocks = [block] + new_blocks;

        tmp = list(zip(points, ids));
        tmp = sorted(tmp, reverse=True);
        points, ids = list(zip(*tmp));
        points, ids = list(points), list(ids);
        
        known_vals = [];
        test_vals = [];
        for i in range(n//block_size+1):
            l = i*block_size;
            r = min((i+1)*block_size, n);
            
            known_vals.append((ids[l:r], points[l:r]));
            test_vals.append((new_blocks[i].user_ids, new_blocks[i].user_points));
        
        self.assertEqual(known_vals, test_vals);
    
    def test_combine(self):
        blocks = [];
        all_ids = [];
        all_points = [];
        
        for j in range(np.random.randint(5,15)):
            n = np.random.randint(10,100);
            
            ids = np.random.randint(low=0, high=10000, size=n);
            points = np.random.randint(low=0, high=10000, size=n);
            
            block = Block();
            for i in range(n):
                block.add_user(ids[i], points[i]);
            
            blocks.append(block);
            all_ids += list(ids);
            all_points += list(points);
            
        tmp = list(zip(all_points, all_ids));
        tmp = sorted(tmp, reverse=True);
        points, ids = list(zip(*tmp));
        points, ids = list(points), list(ids);
        
        for i in range(1, len(blocks)):
            blocks[0].combine(blocks[i]);
        
        known_vals = (points, ids);
        test_vals = (blocks[0].user_points, blocks[0].user_ids);
        
        self.assertEqual(known_vals, test_vals);
    
    def test_delete(self):
        block = Block();

        n = 53;
        ids = np.random.randint(low=1, high=10000, size=n);
        points = np.random.randint(low=1, high=10000, size=n);

        for i in range(n):
            block.add_user(ids[i], points[i]);
        
        for i in range(n):
            if np.random.uniform() < 0.2:
                block.delete_user(ids[i]);
                ids[i] = 0;
                points[i] = 0;
        
        ids = ids[ids!=0];
        points = points[points!=0];
        
        tmp = list(zip(points, ids));
        tmp = sorted(tmp, reverse=True);
        points, ids = list(zip(*tmp));

        known_vals = (list(ids), list(points));
        test_vals = (block.user_ids, block.user_points);

        self.assertEqual(known_vals, test_vals);

if __name__ == '__main__':
    unittest.main();
