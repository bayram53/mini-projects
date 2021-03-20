from User import User;
from Block import Block;

class Leaderboard:
    success = "Success";
    generated_block_id = 0;
    
    def __init__(self):
        self.small_size, self.mid_size, self.large_size = 10, 100, 1000;
        self.users = {};
        self.blocks = {};
        self.sorted_block_ids = [self.__add_new_block()];
    
    def bulk_loading(self, data):
        """
        deletes all previos data and put new data
        """
        
        n = len(data);
        
        if n > 10000:
            self.mid_size = int(n**0.5);
            self.small_size = self.mid_size//10;
            self.large_size = self.mid_size*10;
        else:
            self.mid_size = 100;
            self.small_size = self.mid_size//10;
            self.large_size = self.mid_size*10;
        
        self.users = {}; 
        self.blocks = {};
        self.sorted_block_ids = [self.__add_new_block()];
        bid = self.sorted_block_ids[0];
        b = self.blocks[bid];
        
        for u in data:
            b.add_user(u['user_id'], u['points'], False);
            self.users[u['user_id']] = User(u['display_name'], u['country'], bid, u['user_id']);
        
        b.update();
        
        self.__check_block(bid);
    
    def get_leaderboard(self):
        ret = [];
        rank = 1;
        
        for block_id in self.sorted_block_ids:
            for user_id in self.blocks[block_id].user_ids:
                user = self.users[user_id];
                
                if len(ret) != 0  and  ret[-1]['points'] != user.point:
                    rank = len(ret)+1;
                
                cur = {};
                cur['rank'] = rank;
                cur['points'] = user.point;
                cur['display_name'] = user.display_name;
                cur['country'] = user.country;
                
                ret.append(cur);
            
        return ret;
    
    def score_submit(self, user_id, score_worth):
        if self.users.get(user_id) == None:
            return f"There is no user with id {user_id}";
        
        self.users[user_id].point += score_worth;
        new_point = self.users[user_id].point;
        old_bid = self.users[user_id].block_id;
        
        # coud be done with binary search
        if new_point > self.blocks[self.sorted_block_ids[0]].max_point:
            new_bid = self.sorted_block_ids[0];
        elif new_point < self.blocks[self.sorted_block_ids[-1]].min_point:
            new_bid = self.sorted_block_ids[-1];
        else:
            for bid in self.sorted_block_ids:
                if self.blocks[bid].min_point <= new_point:
                    new_bid = bid;
                    break;
        
        self.blocks[old_bid].delete_user(user_id);
        self.blocks[new_bid].add_user(user_id, new_point);
        self.users[user_id].block_id = new_bid;
        
        self.__check_block(old_bid);
        self.__check_block(new_bid);
        
        return self.success;
    
    def __check_block(self, block_id):
        if self.blocks[block_id].n_users < self.small_size:
            self.__combine(block_id);
        elif self.blocks[block_id].n_users > self.large_size:
            self.__divide(block_id);
    
    def __combine(self, block_id):
        if len(self.blocks) == 1:
            return;
        
        other_id = self.sorted_block_ids[0];
        if other_id == block_id:
            other_id = self.sorted_block_ids[1];
        
        self.blocks[other_id].combine(self.blocks[block_id]);
        self.blocks.pop(block_id);
        self.__update_users(other_id);
        self.__update_sorted_list();
        
        if self.blocks[other_id].n_users > self.large_size:
            self.__divide(other_id);
        
    def __divide(self, block_id):
        new_blocks = self.blocks[block_id].divide(self.mid_size);
        for block in new_blocks:
            new_id = self.__get_new_block_id();
            self.blocks[new_id] = block;
            self.__update_users(new_id);
        
        self.__update_sorted_list();
    
    def __update_users(self, block_id):
        for uid in self.blocks[block_id].user_ids:
            self.users[uid].block_id = block_id;
    
    def get_user(self, user_id):
        if self.users.get(user_id) == None:
            return f"There is no user with id {user_id}";

        user = self.users[user_id];
        n_small = 0;
        ret = {};

        for bid in self.sorted_block_ids:
            if bid != user.block_id:
                n_small += self.blocks[bid].n_users;
                if user.point == self.blocks[bid].min_point:
                    n_small -= self.blocks[bid].n_users_min;
            else:
                for point in self.blocks[bid].user_points:
                    if point > user.point:
                        n_small += 1;
                break;
        
        ret['rank'] = n_small+1;
        ret['points'] = user.point;
        ret['display_name'] = user.display_name;
        ret['country'] = user.country;
        return ret;

    
    def add_user(self, display_name, country):
        user = User(display_name, country);
        self.users[user.id] = user;
        bid = self.sorted_block_ids[-1];
        user.block_id = bid;
        
        self.blocks[bid].add_user(user.id, user.point);
        self.__check_block(bid);
        
        if len(self.users) > 2 * (self.mid_size**2):
            self.mid_size = int(len(self.users)**0.5);
            self.small_size = self.mid_size//10;
            self.large_size = self.mid_size*10;
        
        return user.id;
    
    def __get_new_block_id(self):
        new_id = Leaderboard.generated_block_id; Leaderboard.generated_block_id += 1;
        return new_id;
    
    def __add_new_block(self):
        new_id = self.__get_new_block_id();
        self.blocks[new_id] = Block();
        return new_id;
    
    def __update_sorted_list(self):
        bids = self.blocks.keys();
        mn_mx = [];
        
        for bid in bids:
            mn_mx.append((self.blocks[bid].max_point, self.blocks[bid].min_point));
        
        tmp = list(zip(bids, mn_mx));
        tmp = sorted(tmp, key=lambda x: x[1], reverse=True);
        bids, _ = list(zip(*tmp));
        
        self.sorted_block_ids = list(bids);
