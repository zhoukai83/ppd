import rsa
import base64

privatekey = '''
-----BEGIN RSA PRIVATE KEY-----
MIICXQIBAAKBgQDDN2K33KPvgHUff4Ta29qvpgmvXvYUwSGoJoBznu7LMmdYZBx+YKUpN8ij7N+dbA1aewb2AG/QlQ6WLUifVw6RhJ6s5V6NoWewes8Pe4NGk6HW8bp4PcxkUVavIOU/YZQHxiNnmeN1Y/X0Dpiuytz7JPg8gq5jbfVX90NKag8VrwIDAQABAoGAXxYxPYF5UIVvh0Ijwj7ojDoB6awFjSJtdGwckTTO96a7c/B/eIc2q5cCYeZVHWauMm5Oe7DGxgB0tG2mPAa5jwlQSJUP19laCBjmc/pnzyY2c1OiGnaTo5AswUmGrO3sz4DoHj2o6WMKTWoZL8VkuCdlq4SNZ6qrKPCR02mnsFECQQDzGfqKhad20Y5R39a494jeoiJAaUm9cTA6SBVoxAixCs4EIZwE63YWPFgeO6uMDzvyD8iefFBT/0ORhjbh2k3VAkEAzZL9BakD3HYC9NXG084+IcNe1a6sOfW5FnYGXadL/BUPHLYMp4AtRaTRnlnB/l7ngRFkpwf4YTNFn6Ix5fIjcwJBALOaturOshnr2s0MphRD9aAeg1W5NBy9WldE2GRtqMo8ZFbTCfTsjXMCJEw545T30F8XYC4PRD26sw357eRRJ/0CQHwub8QMjjWN4ElQHhRygNvabh48rvMwOYeU8lF+rwrvGbrpSgmhBzgL0UiLxgFICSbRf/DagrMMyuEclHHobHsCQQCIxPQdcZ0iXTBN6iGuE6XwXfHFL9zjOVrWhfqTCCs/NMtZmC0uVLYcY1tRjabBJg543Zo9RO356GtWTaQkHgIK
-----END RSA PRIVATE KEY-----
'''

publickey = ""


class rsa_client:
    '''''
    RSA签名
    '''

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
