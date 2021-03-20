import unittest;
import sys;
import numpy as np;
sys.path.append('../main');

from User import User;

class TestUser(unittest.TestCase):
    def test_user(self):
        tmp = {};
        tmp['display_name'] = 'deneme';
        tmp['country'] = 'tr';
        tmp['point'] = 40;
        tmp['block_id'] = 53;

        user = User(display_name=tmp['display_name'], country=tmp['country'], block_id=tmp['block_id']);

        user.update_score(+40);

        tmp_user = {};
        tmp_user['display_name'] = user.display_name;
        tmp_user['country'] = user.country;
        tmp_user['block_id'] = user.block_id;
        tmp_user['point'] = user.point;

        self.assertEqual(tmp, tmp_user);

