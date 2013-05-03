import unittest
import tempfile
import os
from pwmngr.manager import PwDb


class TestPwDb(unittest.TestCase):
    def setUp(self):
        handle = tempfile.NamedTemporaryFile(delete=False)
        self.tempdb = handle.name
        handle.close()

        self.pwdb = PwDb(self.tempdb)
        key, self.plain = "thiskey", "thispwd"        
        self.pwdb.set_key(key, self.plain, "pass")

    def tearDown(self):
        os.remove(self.tempdb)


    def test_get_pwd(self):
        dpwd = self.pwdb.get_key("thiskey", "pass")
        self.assertEqual(self.plain, dpwd)

    def test_wrong_master(self):
        dpwd = self.pwdb.get_key("thiskey", "wrong")
        self.assertTrue(len(dpwd)==0)

    def test_wrong_key(self):
        with self.assertRaises(KeyError):
            self.pwdb.get_key("dontexists", "pass")
            

    # def test_lot_of_keys(self):
    #     keys = ["blah-%d-hlab"%i for i in xrange(10)]
    #     for k in keys :
    #         self.pwdb.set_key(k,"pass","master_password")
    #     # completely reload the file
    #     otherdb = PwDb(self.tempdb)
    #     otherdb.parse_file()
    #     for k in keys:
    #         self.assertEqual(otherdb.get_key(k,"master_password"), "pass")
            
if __name__ == '__main__':
    unittest.main()
