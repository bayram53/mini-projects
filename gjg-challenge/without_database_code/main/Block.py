from functools import cmp_to_key

class Block:
    """
    Block class is used to contain group of users. Block only contains ids and points of users.
    """
    def __init__(self):
        self.user_ids = []
        self.user_points = [];
        self.n_users = 0;
        self.min_point = -1;
        self.max_point = -1;
        self.n_users_min = 0;
    
    
    def sort(self):
        """
        Sorts the users in this block by points in decreasing order.
        Parameter: None
        Returns: None
        """
        tmp = list(zip(self.user_points, self.user_ids));
        tmp = sorted(tmp, reverse=True);
        self.user_points, self.user_ids = list(zip(*tmp));
        
        self.user_points = list(self.user_points);
        self.user_ids = list(self.user_ids);
    
    def update(self):
        """
        This method should be called after adding user to block i.e update block values such as min_point max_point, ...
        Parameter: None
        Returns: None
        """
        
        if self.n_users == 0:
            self.n_users_min = 0;
            return;
        
        self.sort();
        
        self.min_point = self.user_points[-1];
        self.max_point = self.user_points[0];

        same_count = 0
        for i in self.user_points:
            if i == self.min_point:
                same_count += 1;
        
        self.n_users_min = same_count;
    
    def add_user(self, user_id, user_point, do_update=True):
        """
        Adds user to this block. Update this block if do_update == True;
        Parameters: user_id, user_point, do_update
        Returns: None
        """
        
        self.n_users += 1;
        self.user_ids.append(user_id);
        self.user_points.append(user_point);
        
        if do_update:
            self.update();
    
    def delete_user(self, user_id):
        target_i = -1;
        for i in range(self.n_users):
            if self.user_ids[i] == user_id:
                target_i = i;
                break;
        
        if target_i != -1:
            self.user_ids.pop(target_i);
            self.user_points.pop(target_i);
            self.n_users -= 1;
            self.update();
    
    
    def divide(self, block_size):
        """
        Divide this block into many small blocks. This should be called when number of users in this block is very high. This block remains and new blocks will be constructed. This block and all new blocks have block_size or less than block_size(only last block) users.
        Parameter: block_size
        Returns: list of new blocks
        """
        new_blocks = [];
        if block_size < self.n_users:
            for i in range(block_size, self.n_users):
                if i % block_size == 0:
                    cur_block = Block();
                    new_blocks.append(cur_block);
                
                cur_block.add_user(self.user_ids[i], self.user_points[i], False);
            
            for block in new_blocks:
                block.update();
            
            self.n_users = block_size;
            self.user_ids = self.user_ids[:block_size];
            self.user_points = self.user_points[:block_size];
            self.update();

        return new_blocks;
    
    def combine(self, other_blocks):
        """
        Combined self and new_blocks and put result on self. new_blocks could be single block or list of blocks
        Parameter: new_blocks (single or list of blocks)
        Returns: None
        """
        if type(other_blocks) == type(self):
            other_blocks = [other_blocks];

        for block in other_blocks:
            for i in range(block.n_users):
                self.add_user(block.user_ids[i], block.user_points[i], False);
        
        self.update();
