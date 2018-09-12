import rsa
import base64

privatekey = '''
-----BEGIN RSA PRIVATE KEY-----
MIICXQIBAAKBgQDDN2K33KPvgHUff4Ta29qvpgmvXvYUwSGoJoBznu7LMmdYZBx+YKUpN8ij7N+dbA1aewb2AG/QlQ6WLUifVw6RhJ6s5V6NoWewes8Pe4NGk6HW8bp4PcxkUVavIOU/YZQHxiNnmeN1Y/X0Dpiuytz7JPg8gq5jbfVX90NKag8VrwIDAQABAoGAXxYxPYF5UIVvh0Ijwj7ojDoB6awFjSJtdGwckTTO96a7c/B/eIc2q5cCYeZVHWauMm5Oe7DGxgB0tG2mPAa5jwlQSJUP19laCBjmc/pnzyY2c1OiGnaTo5AswUmGrO3sz4DoHj2o6WMKTWoZL8VkuCdlq4SNZ6qrKPCR02mnsFECQQDzGfqKhad20Y5R39a494jeoiJAaUm9cTA6SBVoxAixCs4EIZwE63YWPFgeO6uMDzvyD8iefFBT/0ORhjbh2k3VAkEAzZL9BakD3HYC9NXG084+IcNe1a6sOfW5FnYGXadL/BUPHLYMp4AtRaTRnlnB/l7ngRFkpwf4YTNFn6Ix5fIjcwJBALOaturOshnr2s0MphRD9aAeg1W5NBy9WldE2GRtqMo8ZFbTCfTsjXMCJEw545T30F8XYC4PRD26sw357eRRJ/0CQHwub8QMjjWN4ElQHhRygNvabh48rvMwOYeU8lF+rwrvGbrpSgmhBzgL0UiLxgFICSbRf/DagrMMyuEclHHobHsCQQCIxPQdcZ0iXTBN6iGuE6XwXfHFL9zjOVrWhfqTCCs/NMtZmC0uVLYcY1tRjabBJg543Zo9RO356GtWTaQkHgIK
-----END RSA PRIVATE KEY-----
'''


privatekey_2 = '''
-----BEGIN RSA PRIVATE KEY-----
MIICWwIBAAKBgQC3b6GQxhVufoR6naWN3kr0q33cocQmKsdtjOamGMJoyaLD+72GW72Sxg0Q76YdwWMiZWJra+1dC6pxMJYB7DIkko58DoN3SVm1LjdkPXaq+OAFcWUUtnCaTL/i3p11knW8XmgyYyYEireBFGwFaw/zKxm9Nhbg5uGOwaPuP4/iQQIDAQABAoGAVvEL7KhWBBbnB46spv8TG8AkWWw6obRo7V14/ISDsFLRWH56p7HXujcwfjR30WaVa/oNmch/qjgbQqa6kpK2eJ2lT19tW8rxmdnAQqImT48YrAJXFWBpvKGRrGmij1fHuyieksMLaNnSXeCWIbrz3oDXNnbOBRrOhfmmnKw+llkCQQDbyKEafNJvWSpUN0VkxVO0EQTDa7taVdilzDJ6tI+6HFDfarFMvpD4LbHTp/qQq0LZssEQUGOOjknuozG14sGPAkEA1am1y0o/cdViBzJGjQ9ppwNtLg5AhhgtLXO2witAQKEhYoaqbjEoIqP8wVFiBgtFpkr8XJgn/QcxToXaEY2XLwJAcp2JLmgD0d+dDHgabzfcs93gLw1CkhSMu8HmXUlGXtcfcbORLKWAsnwZ7Xf/WmyFm0P2HMzfbltTwOhIJ0NOjwJAcMoZ8arMOydNjEb5/1T3jPa+F+XmIeN5VdkTzQRP8s4cdYppRaolacPvlY2ElXQ13EcRWT/pPCUj3jPCnimEeQJAE+ukIXgNEkF2tZxf4SAbBqCCOVmFzSkZmJLYzbPjfTg4NMBZqT/9BMeh16mMcjZBio8ClYJV8XFqoZ7v9WWN7g==
-----END RSA PRIVATE KEY-----
'''
publickey = ""


class RsaClient:
    def __init__(self, private_key):
        self.private_key = private_key

    '''''
    RSA签名
    '''

    def sign(self, signdata):
        '''''
        @param signdata: 需要签名的字符串
        '''
        signdata = signdata.lower().encode('utf-8')
        PrivateKey = rsa.PrivateKey.load_pkcs1(self.private_key)
        rsa_sign = rsa.sign(signdata, PrivateKey, 'SHA-1')
        signature = base64.b64encode(rsa_sign)
        return signature

    def sort(self, dicts):
        '''''
        作用类似与java的treemap,
        取出key值,按照字母排序后将keyvalue拼接起来
        返回字符串
        '''
        dics = sorted(dicts.items(), key=lambda k: k[0])
        params = ""
        for dic in dics:
            if type(dic[1]) is str:
                params += dic[0] + dic[1]
        return params

    def encrypt(self, encryptdata):
        PublicKey = rsa.PublicKey.load_pkcs1_openssl_pem(publickey)
        # PublicKey = rsa.PublicKey.load_pkcs1(Global.publickey)
        encrypted = base64.b64encode(rsa.encrypt(encryptdata, PublicKey))
        return encrypted

    def decrypt(self, decryptdata):
        PrivateKey = rsa.PrivateKey.load_pkcs1(self.private_key)
        # decrypted = base64.b64decode(rsa.decrypt(decryptdata, PrivateKey))
        decrypted = rsa.decrypt(base64.b64decode(decryptdata), PrivateKey)
        return decrypted


    @staticmethod
    def sign(signdata):
        '''''
        @param signdata: 需要签名的字符串
        '''
        signdata = signdata.lower().encode('utf-8')
        PrivateKey = rsa.PrivateKey.load_pkcs1(privatekey)
        rsa_sign = rsa.sign(signdata, PrivateKey, 'SHA-1')
        signature = base64.b64encode(rsa_sign)
        return signature

    #

    @staticmethod
    def sort(dicts):
        '''''
        作用类似与java的treemap,
        取出key值,按照字母排序后将keyvalue拼接起来
        返回字符串
        '''
        dics = sorted(dicts.items(), key=lambda k: k[0])
        params = ""
        for dic in dics:
            if type(dic[1]) is str:
                params += dic[0] + dic[1]
        return params

    @staticmethod
    def encrypt(encryptdata):
        PublicKey = rsa.PublicKey.load_pkcs1_openssl_pem(publickey)
        # PublicKey = rsa.PublicKey.load_pkcs1(Global.publickey)
        encrypted = base64.b64encode(rsa.encrypt(encryptdata, PublicKey))
        return encrypted

    @staticmethod
    def decrypt(decryptdata):
        PrivateKey = rsa.PrivateKey.load_pkcs1(privatekey)
        # decrypted = base64.b64decode(rsa.decrypt(decryptdata, PrivateKey))
        decrypted = rsa.decrypt(base64.b64decode(decryptdata), PrivateKey)
        return decrypted
