import nacl.signing
import nacl.encoding
import nacl.secret

class KeyStore(object):
    skey = "%s.skey"
    vkey = "%s.vkey"

    def get_signing_key(self, fingerprint):
        data = self.pyfs.getcontents(self.skey % fingerprint)
        return nacl.signing.SigningKey(data)

    def get_verify_key(self, fingerprint):
        data = self.pyfs.getcontents(self.vkey % fingerprint)
        return nacl.signing.VerifyKey(data)

def generate_signing_key():
    return nacl.signing.SigningKey.generate()

HexEncoder = nacl.encoding.HexEncoder
RawEncoder = nacl.encoding.RawEncoder
