class Block:
    def __init__(self, block_id, db):
        self.block_id = block_id;
        self.db = db;
    
    @staticmethod
    def get_cmp(user_id, user_point):
        # TODO change this in order to get different consistence sorting
        #point = round(user_point + 1e-6, 7)
        #return '0'*(20-len(str(point))) + str(point) + chr(0) + str(user_id);
        return user_point
    
    def add_user(self,  user_id, user_point):
        """
        Adds user to this block.
        
        Parameters
        ----------
        user_id : ObjectId
        user_point : int

        Returns
        -------
        None.

        """
        cmp_val = Block.get_cmp(user_id, user_point)
        
        self.db['blocks'].update_one(
                   {'_id': self.block_id},
                   {'$push' : 
                    {'users': { 
                     '$each': [{'id': user_id, 'points': user_point, 'cmp_val': cmp_val}],
                     '$sort': {'cmp_val': -1}}}
                   }
               );
            
        self.db['users'].update_one(
                   {'_id': user_id},
                   {'$set' : {'block_id': self.block_id}}
               );
        
        Block.update(self.db, self.block_id);
    
    def delete_user(self, user_id):
        """
        Deletes user from this block

        Parameters
        ----------
        user_id : ObjectId

        Returns
        -------
        None.

        """
        # delete user info
        self.db['blocks'].update_one(
                   {'_id': self.block_id},
                   {'$pull' : 
                    {'users': {'id': user_id},
                   }}
               );
        
        # sort users
        self.db['blocks'].update_one(
                   {'_id': self.block_id},
                   {'$push' : 
                    {'users': { 
                     '$each': [],
                     '$sort': {'cmp_val': -1}}}
                   }
               );
        
        Block.update(self.db, self.block_id);
            
    def get_users(self):
        """
        Gives this block's userIds and points sorted according points

        Returns
        -------
        TYPE
            list of objectIds and int pair i.e [[upoint1,uid1], [upoint2,uid2], ...].

        """
        res = self.db['blocks'].find_one({'_id': self.block_id});
        if res is not None:
            return res['users'];
        return [];
    
    def divide(self, desired_size):
        """
        Divides this block into multiple blocks where each block have desired_size users except last one.

        Parameters
        ----------
        desired_size : int
            desired number of users on each block.

        Returns
        -------
        TYPE
            list of block_ids of new blocks [bid1, bid2, ...].

        """
        users = self.get_users(); 
        n = len(users);
        
        new_lists = [];
        for k in range(0,n):
            a, b = k*desired_size, min(n, (k+1)*desired_size);
            new_lists.append(users[a:b]);
            if b == n:
                break;
        
        ids = [self.block_id];
        for i in range(1, len(new_lists)):
            ids.append(self.db['blocks'].insert_one({}).inserted_id);
            
        for i in range(len(new_lists)):
            for x in new_lists[i]:
                uid = x['id'];
                self.db['users'].update_one(
                   {'_id': uid},
                   {'$set' : {'block_id': ids[i]}},
               );
            
            self.db['blocks'].update_one(
                {'_id': ids[i]},
                {'$set': {'users': new_lists[i]}}
            );
            Block.update(self.db, ids[i]);
            
            
        
        return ids[1:];
    
    def combine(self, block_id):
        """
        Combines this block with other block and put combined block in other block. This block will be destroyed.

        Parameters
        ----------
        block_id : block_id of other block

        Returns
        -------
        None.

        """
        users = self.get_users(); 
        
        self.db['blocks'].update_one(
                   {'_id': block_id},
                   {'$push' : 
                    {'users': { 
                     '$each': users,
                     '$sort': {'cmp_val': -1}}}
                   }
               );
        Block.update(self.db, block_id);
        
        for x in users:
            uid = x['id'];
            self.db['users'].update_one(
                   {'_id': uid},
                   {'$set' : {'block_id': block_id}}
               );
        
        self.db['blocks'].delete_one({'_id': self.block_id});
    
    @staticmethod
    def update(db, block_id):
        tmp = db['blocks'].aggregate([
            {'$match': { '_id': block_id }},
            {'$addFields' :{
                'first_cmp': {'$first': '$users.cmp_val'},
                'last_point': {'$last': '$users.points'},
                'n_users': {'$size': '$users'},
                }
            }]);
        
        for i in tmp:
            try:
                first_cmp, last_point, n_users = i['first_cmp'], i['last_point'], i['n_users'];
                break;
            except:
                db['blocks'].delete_one({'_id': block_id});
                return;
        
        db['blocks'].update_one(
            {'_id': block_id},
            {'$set': {'first_cmp': first_cmp, 'last_point': last_point, 'n_users': n_users}}
            );
            