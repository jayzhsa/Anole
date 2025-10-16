__author__ = 'Sisi'

import hmac
import hashlib

class HMAC_KEY:
    def __init__(self):
        self.k = bytes('the shared secret key here').encode('utf-8') 
        #we are just using the same key now
        #TODO: extend this to have multiple keys
    
    def __del__(self):
        self.k = None
    
    def gen_hmac(self,content):
        return hmac.new(self.k, content, hashlib.sha256).digest()
    
    def verify(self,mac,content):
        #return hmac.compare_digest(mac, hmac.new(self.k, content, hashlib.sha256).digest())
        return str(mac)==str(hmac.new(self.k, content, hashlib.sha256).digest())