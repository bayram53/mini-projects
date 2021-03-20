import unittest;
import sys;
import numpy as np;
sys.path.append('../main');
import time;

from Block import Block;
from User import User;
from Leaderboard import Leaderboard;

class TestLeaderboard(unittest.TestCase):
    def sort(self, users):
        list_keys = [];
        list_points = [];
        for k,v in users.items():
            list_keys.append(k);
            list_points.append(v['points']);
        
        tmp = list(zip(list_points, list_keys));
        tmp = sorted(tmp, reverse=True);
        points, uids = list(zip(*tmp));
        
        rank = 0;
        prev = -1;
        ret = [];
        for i in range(len(uids)):
            if points[i] != prev:
                rank = i+1;
                prev = points[i];
            users[uids[i]]['rank'] = rank;
            ret.append(users[uids[i]]);
        return ret;
            
    
    def test_get_user(self):
        users, board = self.generate_random_test(1000);
        
        for i in range(1000):
            num = np.random.uniform();
            n = len(users);
            uid = list(users.keys())[np.random.randint(0,n)];
            
            if num > 0.5:
                score_worth = np.random.randint(10,100);
                board.score_submit(uid, score_worth);
                users[uid]['points'] += score_worth;
            else:
                test_user = board.get_user(uid);
                known_user = users[uid];
                rank = 0
                for u in users.values():
                    if u['points'] > users[uid]['points']:
                        rank += 1;
                known_user['rank'] = rank+1;
                
                self.assertEqual(known_user, test_user);
                
    def compare(self, la, lb):
        prev_rank = -1;
        a = [];
        b = [];
        
        self.assertTrue(len(la) == len(lb));
        
        la.append({'rank': -2});
        lb.append({'rank': -2});
        
        for i in range(len(la)):
            if la[i]['rank'] != prev_rank:
                a = sorted(a, key=lambda x: x['display_name']+x['country']);
                b = sorted(b, key=lambda x: x['display_name']+x['country']);
                self.assertEqual(a, b);
                
                a = [];
                b = [];
                rank = la[i]['rank'];
                
        
    def test_all_small(self):
        n = 1000;
        users, board = self.generate_random_test(n);
        
        known = self.sort(users);
        #self.assertEqual(known, board.get_leaderboard());
        self.compare(known, board.get_leaderboard());
    
    def test_all_large(self):
        n = 1000;
        users, board = self.generate_random_test(n);

        known = self.sort(users);
        #self.assertEqual(known, board.get_leaderboard());
        self.compare(known, board.get_leaderboard());
    
    def get_random_string(self, n):
        ret = "";
        for i in range(n):
            ret += chr(ord('a')+np.random.randint(0,26));
        return ret;
    
    def test_bulk_loading(self):
        n = 10000002;
        users = [];
        dict_users = {};
        points = np.random.randint(low=1, high=n//100, size=n);
        display_names = np.random.randint(low=1, high=n*10, size=n);
        countries = np.random.randint(low=1, high=200, size=n);
        
        for i in range(n):
            u = {'points': points[i], 'user_id': i, 'display_name': display_names[i], 'country': countries[i]};
            users.append(u);
            dict_users[u['user_id']] = u;
        
        board = Leaderboard();
        board.bulk_loading(users);
        known = self.sort(dict_users);
        self.compare(known, board.get_leaderboard());
        
        n_ops = 10;
        mx = 0;
        start = time.time();
        for i in range(n_ops):
            s1 = time.time();
            num = np.random.uniform();
            if num < 0.25: # score_submit
                board.score_submit(np.random.randint(n), np.random.randint(1,100));
            elif num < 0.5: # get user
                board.get_user(np.random.randint(n));
            elif num < 0.75: # add user
                board.add_user(np.random.randint(n), np.random.randint(1,100));
            else:
                tmp = board.get_leaderboard();
            e1 = time.time()
            mx = max(mx, e1-s1);
        
        end = time.time()
        print('\n\tmax elapsed time is {:.3f}'.format(mx));
        print('\taverage time spent {:.3f}'.format((end-start)/n_ops));
        
    
    def generate_random_test(self, n_ops):
        users = {};
        board = Leaderboard();
        
        for i in range(n_ops):
            num = np.random.uniform();
            if num > 0.9: # add_user
                name = self.get_random_string(10);
                country = self.get_random_string(2);
                new_id = board.add_user(name, country);
                users[new_id] = {'country': country, 'display_name': name, 'points': 0};
            else: # score_submit
                n = len(users);
                if n == 0: 
                    continue;
                uid = list(users.keys())[np.random.randint(0,n)];
                score_worth = np.random.randint(10,100);
                board.score_submit(uid, score_worth);
                users[uid]['points'] += score_worth;
        
        return users, board;
                
        
        
if __name__ == '__main__':
    unittest.main();
