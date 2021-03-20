class User:
    n_users = 0;
    def __init__(self, display_name, country, block_id=-1, uid=-1):
        self.display_name = display_name;
        if uid == -1:
            self.id = User.n_users; User.n_users +=1;
        else:
            self.id = uid;
        self.country = country;
        self.point = 0;
        self.block_id = block_id;
    
    def update_score(self, score_worth):
        self.point += score_worth;
        
    
