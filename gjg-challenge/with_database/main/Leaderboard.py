from flask import Flask;
from flask import request;
from database import Connect;
from Block import Block;
from bson import ObjectId
import pdb;
import time;
from flask import jsonify
from flask import Response
import json
import uuid;

app = Flask(__name__)
database = Connect();
all_countries = 'all_countries';
EPS = 1e-6

sizes = {
    'small': 200,
    'mid': 500,
    'large': 700
    };

@app.route('/leaderboard', methods=['GET'])
def get_leaderboard():
    return __leaderboard(database.get_db(all_countries));
    
@app.route('/leaderboard/<string:country>', methods=['GET'])
def get_country_leaderboard(country):
    return __leaderboard(database.get_db(country));

def __leaderboard(db):
    b_infos = block_infos(db);
    ret = [];
    r = 1; prev = -1; same_cnt = 0;
    for b in b_infos:
        tmp = db['blocks'].find_one({'_id': b['_id']});
        if tmp is None: continue;
        for u in tmp['users']:
            if abs(u['points'] - prev) > EPS:
                prev = u['points'];
                r += same_cnt;
                same_cnt = 0;
            same_cnt += 1;
            
            tmp = user_db(db, u['id']);
            #tmp['user_id'] = str(u['id']);
            tmp['rank'] = r;
            tmp.pop('_id'); tmp.pop('block_id');
            ret.append(tmp)
    return Response(json.dumps(ret),  mimetype='application/json');
    
    
@app.route('/score/submit', methods=['POST'])
def update_score():
    request_data = request.get_json();
    user_id = request_data['user_id'];
    score_worth = request_data['score_worth'];
    #timestamp = request_data['timestamp'];

    tmp_user = user_db(database.get_db(all_countries), user_id);
    country = tmp_user['country'];
    
    __update_user(database.get_db(all_countries), user_id, score_worth);
    __update_user(database.get_db(country), user_id, score_worth);
    
    ret = {};
    ret['timestamp'] = str(int(time.time()));
    ret['user_id'] = str(user_id);
    ret['score_worth'] = score_worth;
    
    return ret;

def __update_user(db, user_id, score_worth):
    user = user_db(db, user_id);
    new_score = user['points'] + score_worth;
    old_bid = user['block_id'];
    cur_cmp = Block.get_cmp(user_id, new_score);
    
    Block(old_bid, db).delete_user(user_id);
    db['users'].update_one(
        {'_id': user_id},
        {'$inc': {'points': score_worth}}
        );
    
    prev_bid = -1;
    new_bid = -1;
    bs = block_infos(db);
    for b in bs:
        if b['first_cmp'] < cur_cmp:
            if prev_bid == -1:
                new_bid = b['_id'];
            else:
                new_bid = prev_bid;
            break;
        prev_bid = b['_id'];
    
    if new_bid == -1:
        new_bid = last_block(db);
    
    Block(new_bid, db).add_user(user_id, new_score);
    
    check_block(db, new_bid);
    check_block(db, old_bid);
    
@app.route('/user/profile/<string:user_id>', methods=['GET'])
def get_user(user_id):
    return __get_user(database.get_db(all_countries), user_id);

def __get_user(db, user_id):
    b_infos = block_infos(db);
    ret = user_db(db, user_id);
    ret.pop('block_id'); ret.pop('_id');
    user_point = ret['points'];
    ret['user_id'] = str(user_id);
    
    rank = 1;
    for b in b_infos:
        if b['last_point'] > user_point  and  abs(b['last_point'] - user_point) > EPS:
            rank += b['n_users'];
        else:
            cur_b = Block(b['_id'], db).get_users();
            for u in cur_b:
                if abs(u['points'] - user_point) > EPS  and  u['points'] > user_point:
                    rank += 1;
            break;
    ret['rank'] = rank;
    return ret;
    
    
@app.route('/user/create', methods=['POST'])
def add_user():
    request_data = request.get_json();
    display_name = request_data['display_name'];
    country = request_data.get('country');
    if country is None:
        country = 'world'
    
    if country == all_countries: return;
    
    ret = __add_user(database.get_db(all_countries), display_name, country);
    
    if not database.have_db(country):
        init_db(database.get_db(country))
    
    __add_user(database.get_db(country), display_name, country, ret['user_id']);
    
    return ret;

@app.route('/user/add_many', methods=['POST'])
def add_many():
    request_data = request.get_json();
    display_names = request_data['display_names'];
    countries = request_data.get('countries');
    n = len(display_names);
    if countries is None:
        countries = ['world']*n;
    
    ret = [];
    for i in range(n):
        display_name = display_names[i];
        country = countries[i];
        cur  = __add_user(database.get_db(all_countries), display_name, country);
        
        if not database.have_db(country):
            init_db(database.get_db(country))
        
        __add_user(database.get_db(country), display_name, country, cur['user_id']);
        
        ret.append(cur);
    
    return Response(json.dumps(ret),  mimetype='application/json');
    
def __add_user(db, display_name, country, user_id=None):
    if user_id is None:
        user_id = str(uuid.uuid4());
    db['users'].insert_one({
        '_id': user_id,
        'display_name': display_name,
        'country': country,
        'points': 0
        })
    bid = last_block(db);
    
    Block(bid, db).add_user(user_id, 0);
    check_block(db, bid);
    
    return __get_user(db, user_id);
    

def last_block(db):
    tmp = db['blocks'].aggregate([
        {'$project': {'_id': 1, 'first_cmp': 1}},
        {'$sort': {'first_cmp': 1}},
        {'$group': {'_id':{}, 'bid': {'$first': '$_id'} }},
        ]);
    
    for i in tmp: return i['bid'];
    return db['blocks'].insert_one({}).inserted_id;
    

def block_infos(db):
    return db['blocks'].aggregate([
        {'$project': {'_id': 1, 'n_users': 1, 'last_point': 1, 'first_cmp': 1}},
        {'$sort': {'first_cmp': -1}}
        ]);

def all_users(db, block_info=False):
    return db['users'].find({});

def user_db(db, user_id):
    return db['users'].find_one({'_id': user_id});
    

def n_blocks(db):
    tmp = db['blocks'].aggregate([{ '$group': { '_id': {}, 'n': { '$sum': 1 } } }]);
    for i in tmp: return i['n'];
    return 0;


def check_block(db, block_id):
    tmp = db['blocks'].find_one({'_id': block_id});
    if tmp is None: return;
    
    if tmp['n_users'] >= sizes['large']:
        Block(block_id, db).divide(sizes['mid']);
        return;
    
    if n_blocks(db) != 1  and  tmp['n_users'] <= sizes['small']:
        prev_bid = -1;
        found = False;
        bs = block_infos(db);
        
        for b in bs:
            if b['_id'] == block_id:
                if prev_bid == -1: # first one
                    found = True;
                else:
                    break;
            else:
                prev_bid = b['_id'];
                if found:
                    break;
        
        Block(block_id, db).combine(prev_bid);


def init():
    None;
    #if database.have_db(all_countries) == False:
    #    init_db(database.get_db(all_countries))
    
def init_db(db):
    None;
    #if db['blocks'].find_one({}) is None:
    #    db['blocks'].insert_one({});

if __name__ == '__main__':
    init();
    #app.run(host='0.0.0.0', port=8080)
    from waitress import serve;
    serve(app, host='0.0.0.0', port=80)
