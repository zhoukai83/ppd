import rsa
import base64

privatekey = '''
-----BEGIN RSA PRIVATE KEY-----
MIICXQIBAAKBgQDDN2K33KPvgHUff4Ta29qvpgmvXvYUwSGoJoBznu7LMmdYZBx+YKUpN8ij7N+dbA1aewb2AG/QlQ6WLUifVw6RhJ6s5V6NoWewes8Pe4NGk6HW8bp4PcxkUVavIOU/YZQHxiNnmeN1Y/X0Dpiuytz7JPg8gq5jbfVX90NKag8VrwIDAQABAoGAXxYxPYF5UIVvh0Ijwj7ojDoB6awFjSJtdGwckTTO96a7c/B/eIc2q5cCYeZVHWauMm5Oe7DGxgB0tG2mPAa5jwlQSJUP19laCBjmc/pnzyY2c1OiGnaTo5AswUmGrO3sz4DoHj2o6WMKTWoZL8VkuCdlq4SNZ6qrKPCR02mnsFECQQDzGfqKhad20Y5R39a494jeoiJAaUm9cTA6SBVoxAixCs4EIZwE63YWPFgeO6uMDzvyD8iefFBT/0ORhjbh2k3VAkEAzZL9BakD3HYC9NXG084+IcNe1a6sOfW5FnYGXadL/BUPHLYMp4AtRaTRnlnB/l7ngRFkpwf4YTNFn6Ix5fIjcwJBALOaturOshnr2s0MphRD9aAeg1W5NBy9WldE2GRtqMo8ZFbTCfTsjXMCJEw545T30F8XYC4PRD26sw357eRRJ/0CQHwub8QMjjWN4ElQHhRygNvabh48rvMwOYeU8lF+rwrvGbrpSgmhBzgL0UiLxgFICSbRf/DagrMMyuEclHHobHsCQQCIxPQdcZ0iXTBN6iGuE6XwXfHFL9zjOVrWhfqTCCs/NMtZmC0uVLYcY1tRjabBJg543Zo9RO356GtWTaQkHgIK
-----END RSA PRIVATE KEY-----
'''

# privatekey = '''
# -----BEGIN RSA PRIVATE KEY-----
# MIICdgIBADANBgkqhkiG9w0BAQEFAASCAmAwggJcAgEAAoGBAJMZPZ0DukRrlkg9wx0BVKjww80PpNoTjNRTou++7+ZxQvCRPIT7ZBmVmbhwUEm94wpzkiv8+qspXgYnpHPzanGPZJmWnPDBi5NvNJOV2e5bMw6QtNcS12/dxGW4nOR3JKzxoQtjst/+RxsWjgmoK+ixFOePDNehx1BZT8FP4XH7AgMBAAECgYBcZTVTQ70jLuTlmY3N0UEpIJoMWvA0XqVN1P76UleDys6+Jqv556H3hAVbWYjE2PYcYX2GDdAx5Lj/arUcc9/+X12CQaVvVcFGl2lhLIu4h8dunr2b6zoer8YKfOwEZLKpOg1dy4vk58jhPbPlLuwt9mtRfPLL0Sdu78dXVAjQIQJBAOVfvIxcG0kBR0PhuH7DNbRHzkxSz5zXqnAN8UzOGXz15shrUQAbVhwh2choEhNpf4ItwsuKIa0VmMHvzEhp1hECQQCkLIrOkQBi2ejP7M6A70ZFeCsUDfuwixlz09sh3lHHhf6H2FPnCtCpkuGbCArnfjpTlIBlra2tx2B+oNHA3QtLAkBH6asQinQXgGoaczNHsuYsfnLEZRYoQ0lxVj236cn97o6LeXHsyaVGrqo79bztDx9l7fjrnYQPYv0AmLEAZwYxAkEAj2UAUHBCIBUozgOOUvurKx5MshWMkqTMNGkE604dq+ITcV+32QOPQa2zNBAQRiXwl/QLOcQ7AKA2XiPlUUlAhQJAOzbYO3Jf0DdgMKyzXrsJIYvvIOJxYdTPCJO+c3cDwqzDFNc31Uzn5rpwPvXgvwC3Vog+KzzwYD4914Y01+EZCg==
# -----END RSA PRIVATE KEY-----
# '''

privatekey2 = '''
-----BEGIN RSA PRIVATE KEY-----
MIICXAIBAAKBgQCBUDp6YFA76M1OiPGChrn42ti5l4iUvpO+SC2v+TXupZLmYPSPZbnEImbigTVGdDb6q4/AA3PNx+OOZnVKSJMz3PKW3ATx+wzhlCN+fZyIVJKvM5mFnauTGxkKlDcQqgxOX4bAaITA7gDJCuygUHg6qHE72Z2AJD1VTCl0lijI7QIDAQABAoGAVhT9SLfS0X7RJSWeeACNzm6I9Us9vZ78JSBRYaKpV1tbZgdG5iqWtk0cZk4TE/qLGuWYRP9HWMZm4kWscK3NZy0d1LAqcqk+/3XBDsem+38fP4s0qgoP9kee1NLKzjtzxstxkRgUE43Mlh2WpKEgDDQ9Z6lKh6Iu7jh9co1edYECQQD0c95eDNGbJQIPHFgE0IrKQZEHPWqIGneDmsen0Glwb38v/GsBFJE3YX3kfm5MWcdEPAC7Bo9aAVUFMSTJtM1hAkEAh2v/TOOc+1lfTRF/h/SAbfzuxP674naKqw5khoAyN5OJWykQT7IS2AoMmlXLlkFzdEzSEVs3n5a/Bf8SQcU7DQJAQePtf0pTQU9TY8FPFFUl4+iSb/IlAfSoXEffIyOxGAZlsQiHyy3BCr1zkqBlmJzmckT+KWtWPnt3cEPT166tYQJAUYga+A7dt5JyRzMuxgrVu+KZWq9HLSxThnMu4K+UDFPeUa0ibej3YWyDc/QNk5QqT63kl6CEl6epsJGGS2TUjQJBAO2/QnFx2eLSveUiGcwWeH48kDaJQHq2VHe7x0MEFdeU+HpCMaVlRLEDndLHowYRfU70OY4s60OTT8sr/oaHAts=
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


    # @staticmethod
    # def sign(signdata):
    #     '''''
    #     @param signdata: 需要签名的字符串
    #     '''
    #     signdata = signdata.lower().encode('utf-8')
    #     # print("static sign")
    #     # from pyasn1.codec.der import decoder
    #     # (priv, _) = decoder.decode(privatekey_2)
    #     # print(priv)
    #
    #     # der = rsa.pem.load_pem(privatekey_2, b('RSA PRIVATE KEY'))
    #     # print(der)
    #     PrivateKey = rsa.PrivateKey.load_pkcs1(privatekey2)
    #     rsa_sign = rsa.sign(signdata, PrivateKey, 'SHA-1')
    #     signature = base64.b64encode(rsa_sign)
    #     return signature
    #
    # @staticmethod
    # def sort(dicts):
    #     '''''
    #     作用类似与java的treemap,
    #     取出key值,按照字母排序后将keyvalue拼接起来
    #     返回字符串
    #     '''
    #     dics = sorted(dicts.items(), key=lambda k: k[0])
    #     params = ""
    #     for dic in dics:
    #         if type(dic[1]) is str:
    #             params += dic[0] + dic[1]
    #     return params
    #
    # @staticmethod
    # def encrypt(encryptdata):
    #     PublicKey = rsa.PublicKey.load_pkcs1_openssl_pem(publickey)
    #     # PublicKey = rsa.PublicKey.load_pkcs1(Global.publickey)
    #     encrypted = base64.b64encode(rsa.encrypt(encryptdata, PublicKey))
    #     return encrypted
    #
    # @staticmethod
    # def decrypt(decryptdata):
    #     PrivateKey = rsa.PrivateKey.load_pkcs1(privatekey)
    #     # decrypted = base64.b64decode(rsa.decrypt(decryptdata, PrivateKey))
    #     decrypted = rsa.decrypt(base64.b64decode(decryptdata), PrivateKey)
    #     return decrypted
