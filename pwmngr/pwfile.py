#
# ----------------------------------------------------------------------------
# "THE BEER-WARE LICENSE" (Revision 42):
# Florent D'halluin <flal@melix.net> wrote this file. As long as you retain this notice you
# can do whatever you want with this stuff. If we meet some day, and you think
# this stuff is worth it, you can buy me a beer in return 
# ----------------------------------------------------------------------------
#
  
import cStringIO as StringIO
import os

# for password generation 

alpha = "abcdefghijklmnopqrstuvwxyz"
specials_chars = "#@$_-!?%=()[]"



class PwStore(object) :

    def read(self, key) :
        # returns h, crypt tuple
        raise NotImplemented

    def store(self, key, h, crypt):
        raise NotImplemented


class PlainFileStore(PwStore) :
    def __init__(self, path=None, force_create = False) :
        self._cache = {}
        if path :
            self.path = path
        else :
            if os.path.isfile(".pwmngr") :
                self.path = ".pwmngr"
            else :
                self.path = os.path.expanduser("~/.pwmngr")
        if not os.path.isfile(self.path) :
            if force_create :
                with open(self.path,'w') as f:
                    pass
            else :
                raise IOError        

        self.parse_file()
        
    def parse_file(self) :
        """ read the file and store it pw dict (crptd) """
        with open(self.path) as f :
            for l in f.readlines() :
                try :
                    key, rest = l.split("  ")
                    hsh, value  = rest.split(" ")
                    self._cache[key] = {"hash":hsh,
                                        "pwd":value}
                except ValueError :
                    continue

    def read(self, key) :
        dat = self._cache.get(key, None)
        if dat :
            return dat['hash'], dat['pwd']
        else :
            return None

    def store(self, key, h, crypt) :
        c = StringIO.StringIO()
        updated = False
        enc_line = "%s  %s %s\n"%(key, h, crypt)
        with open(self.path,'r') as f:
            for l in f :
                key_ , rest = l.split("  ")
                if key_ == key :
                    c.write(enc_line)
                    updated = True
                else :
                    c.write(l)
        if not updated :
            c.write(enc_line)
        # also update in memory reprsentation
        self._cache[key] = {"hash":h, "pwd":crypt}
        with open(self.path,'w') as f :
            f.write(c.getvalue())



