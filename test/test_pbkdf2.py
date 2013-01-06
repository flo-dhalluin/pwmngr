from pwmngr.pbkdf2 import pbkdf2
import unittest

class TestPBKDF2(unittest.TestCase):
    def setUp(self):
        pass

    def tearDown(self):
        pass

    def test_pbkdf2(self):
        # ok, there must be some test vectors somewhere else
        keytest = pbkdf2(b'password',b'salt',c=1,target_len=20)
        self.assertEqual(len(keytest), 20)
        hkeytest = [hex(ord(b)) for b in keytest]
        self.assertEqual(hkeytest[0], '0xc')
        self.assertEqual(hkeytest[-1], '0xa6')
        keytest = pbkdf2(b'password',b'salt',c=4096,target_len=20)
        hkeytest = [hex(ord(b)) for b in keytest]
        self.assertEqual(hkeytest[0], '0x4b')
        self.assertEqual(hkeytest[-1], '0xc1')

if __name__ == '__main__':
    unittest.main()

