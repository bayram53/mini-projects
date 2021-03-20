
import requests;
import pdb;
import unittest;
from random import uniform, randint;
import copy;
from collections import defaultdict
import sys;
sys.path.append('../main');
from database import Connect;

EPS = 1e-6;

"""
url = 'http://0.0.0.0:105/user/add_many'
params = {'display_names': ['a', 'b', 'c'],
          'countries': ['tr', 'tr', 'us']};
r = requests.post(url = url, json = params);
data = r.json() 
print(data)
"""

"""
url1 = 'http://0.0.0.0:105/user/create'
params1 = {'display_name': 'fd',
          'country_iso_code': 'tr'};
r = requests.post(url = url1, json = params1);
data = r.json() 
user_id = data['user_id'];

url2 = 'http://0.0.0.0:105/score/submit'
params2 = {'user_id': user_id,
          'score_worth': 2134.3};

r = requests.post(url = url2, json = params2);
data = r.json() 
print(data);


url = 'http://0.0.0.0:105/leaderboard/g';
r = requests.get(url);
print(r.json())


url0 = 'http://0.0.0.0:105/user/profile/' + user_id;
r = requests.get(url0);
print(r.json())
"""

def add_user(display_name, country):
    url = 'http://0.0.0.0:105/user/create'
    params = {'display_name': display_name,
              'country': country};
    r = requests.post(url = url, json = params);
    return r.json();
    
def update_score(user_id, score_worth):
    url = 'http://0.0.0.0:105/score/submit'
    params = {'user_id': user_id,
              'score_worth': score_worth};
    return requests.post(url=url, json=params).json();


def get_user(user_id):
    url = 'http://0.0.0.0:105/user/profile/' + user_id;
    r = requests.get(url);
    return r.json();

def get_leaderboard(country=''):
    url = 'http://0.0.0.0:105/leaderboard'
    if country != '':
        url += '/' + country;
    r = requests.get(url);
    return r.json();

def delete_all_db():
    c = Connect();
    for db_name in c.get_db_names():
        if db_name == 'admin' or db_name == 'local': continue;
        c.client.drop_database(db_name)

class TestLeaderBoard(unittest.TestCase):    
    def test_add_user(self):
        delete_all_db();
        n = 30;
        users = {}
        ids = [];
        countries = set();
        
        for j in range(2):
            # /add/user
            for i in range(n):
                display_name = str(randint(0, 1000000));
                country = chr(ord('a')+randint(0, 25));# + chr(ord('a')+randint(0, 25))
                res = add_user(display_name, country);
                uid = res['user_id'];
                users[uid] = {'user_id': uid, 'display_name': display_name, 'country': country, 'points': 0};
                ids.append(uid);
                countries.add(country);
                
                gt_res = copy.deepcopy(users[uid]);
                gt_res['rank'] = self.get_rank(users, uid);
                #gt_res.pop('country');
                
                self.check(gt_res, res);
            
            # /score/submit
            for i in range(n):
                score_worth = round(uniform(0,1), 2) * 10;
                uid = ids[randint(0, len(ids)-1)];
                res = update_score(uid, score_worth);
                users[uid]['points'] += score_worth;
                
                gt_res = {'user_id': uid, 'score_worth': score_worth};
                res.pop('timestamp');
                
                self.check(gt_res, res);
                
            # get_user
            for i in range(n):
               uid = ids[randint(0, len(ids)-1)];
               
               gt_res = copy.deepcopy(users[uid]);
               gt_res['rank'] = self.get_rank(users, uid);
               #gt_res.pop('country');
               
               self.check(gt_res, get_user(uid));
            
            ld = self.get_ld(users, remove_id=True);
            
            self.check(ld, get_leaderboard());
            for c in countries:
                cur = [];
                for u in ld:
                    if u['country'] == c:
                        cur.append(u);
                prev = -1; cnt_prev = 0; r = 1;
                for u in cur:
                    if abs(prev - u['points']) > 1e-6:
                        r += cnt_prev;
                        cnt_prev = 0;
                        prev = u['points'];
                    cnt_prev += 1;
                    u['rank'] = r;
                
                self.check(cur, get_leaderboard(c));
                
    def check(self, a, b):
        if type(a) == list:
            _a = defaultdict(set); _b = defaultdict(set);
            for i in a: _a[i['rank']].add(tuple(i.items()));
            for i in b: _b[i['rank']].add(tuple(i.items()));
            a = _a; b = _b;
        self.assertEqual(a, b);
    
    def get_rank(self, users, user_id):
        A = self.get_ld(users);
        for i in A:
            if i['user_id'] == user_id:
                return i['rank'];
        return -1;
    
    def get_ld(self, users, remove_id=False):
        users = copy.deepcopy(users);
        u = list(users.values());
        u.sort(key = lambda x: (x['points'], x['user_id']), reverse=True);
        r = 1; prev = -1; cnt_prev = 0;
        
        for i in u:
            if abs(i['points']-prev) > EPS:
                r += cnt_prev;
                prev = i['points'];
                cnt_prev = 0;
            cnt_prev += 1;
            i['rank'] = r;
            if remove_id == True:
                i.pop('user_id');
        
        return u;
        
if __name__ == '__main__':
    unittest.main(); 
    None;