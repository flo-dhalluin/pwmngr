#
# ----------------------------------------------------------------------------
# "THE BEER-WARE LICENSE" (Revision 42):
# Florent D'halluin <flal@melix.net> wrote this file. As long as you retain this notice you
# can do whatever you want with this stuff. If we meet some day, and you think
# this stuff is worth it, you can buy me a beer in return 
# ----------------------------------------------------------------------------
#

from Crypto.Cipher import AES
from Crypto import Random
from pbkdf2 import pbkdf2
import base64
import hashlib
import random
import getpass
import time

from pwfile import PlainFileStore

# for password generation 

alpha = "abcdefghijklmnopqrstuvwxyz"
specials_chars = "#@$_-!?%=()[]"


def generate_password(length=15) :
    """
    generate a random password of length + 2 random digits
    """
    random.seed(Random.new().read(6))
    # make sure we have 2 digits 
    dig = str(random.randint(10,100))
    book = alpha + alpha.upper() + specials_chars
    alph = "".join([random.choice(book) for _ in range(length - 2)])
    return alph + dig 

# padding functions for AES, so that the given
# string is padded to multiple of bytes_num bytes
def crypto_pad(txt,bytes_num) :
    r = len(txt)%bytes_num
    b =  bytes_num - r
    pad = b"".join([chr(b)]*b)
    return txt+pad

def crypto_unpad(txt, bytes_num) :
    r = ord(txt[-1])
    return txt[:-r]


class PwDb :
    def __init__(self,path=None,force_create = False):
        self.pwdb = PlainFileStore(path, force_create)


    def _get_pwd(self,h, master_password) :
        if master_password == None :
            pawd = getpass.getpass("password :")
        else :
            pawd = master_password
        return pbkdf2(pawd, h)
        
    def has_key(self,key) :
        return key in self.pwdb

    def set_key(self,key,passwd, master_password=None) :
        crypt, h = self.crypt(passwd, master_password)
        self.pwdb.store(key, h, crypt)

    def get_key(self,key, master_password=None) :
        d = self.pwdb.read(key)
        if d :
            return self.decrypt(d[1],d[0], master_password)
        else :
            raise KeyError


    def crypt(self,pwd, master_password) :
        """
        encrypt pwd with the provided master_password
        """
        h = hashlib.sha1(str(time.time())).digest()
        derived_password = self._get_pwd(h, master_password)
        ciph = AES.new(derived_password,mode=AES.MODE_CBC,IV=chr(0)*16)
        plain = crypto_pad(pwd,16)
        cryptd = ciph.encrypt(plain)
        return base64.b64encode(cryptd), base64.b64encode(h)

    def decrypt(self,crypt, h, master_password=None):
        dp = self._get_pwd(base64.b64decode(h), master_password)
        ciph = AES.new(dp,mode=AES.MODE_CBC,IV=chr(0)*16)
        plain = ciph.decrypt(base64.b64decode(crypt))
        plain = crypto_unpad(plain,16)
        return plain

def main() :

    import argparse

    try :
        import gtk
        cb = gtk.Clipboard()
    except :
        cb = None 

    parser = argparse.ArgumentParser()
    parser.add_argument("key",nargs=1,help="the key you want to set or retrieve [default action]")
    parser.add_argument("-f","--file",help="the password file (default ~/.pwmngr)")
    parser.add_argument("-g","--generate",action="store_true",help="generate a random password instead of prompting you for the password when setting passwords")
    parser.add_argument("-v","--show", action="store_true",help="default pwmngr store the clear password to clipboard. if set diplay the clear password to stdout")
    parser.add_argument("-s","--set",action="store_true", help="set a password") # get by default ..
    conf = parser.parse_args()

    def output(pwd) :
        if conf.show :
            print pwd
        elif cb :
            cb.set_text(pwd)
            cb.store()
            print "pwd stored to clipboard"
        else :
            print "I cannot talk to a clipboard use --show option explicitely please"
            exit(0)

    def askYorexit(msg) :
            a = raw_input(msg)
            if(a.upper() == 'Y') :
                return True
            else :
                print "aborting"
                exit(1)

        
    try :
        p = PwDb(conf.file)
    except IOError :
        askYorexit("password file does not exist, do you want to create one ? [N/y]")
        p = PwDb(conf.file, True)

    if(conf.set) :
        if conf.generate :
            pwd = generate_password()
            output(pwd)

        else :
            pwd = getpass.getpass("password to store :")
        if(not p.has_key(conf.key[0])):
            p.set_key(conf.key[0],pwd) 
        else :
            askYorexit("key already exists overwrite ? [N/y]")
            p.set_key(conf.key[0],pwd)
    else :
        pwd = p.get_key(conf.key[0])
        output(pwd)
    

if __name__ == '__main__':
    main()    
