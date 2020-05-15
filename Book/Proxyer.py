import requests

from Book.ProxyGetter import ProxyGetter


class Proxyer:
    def __init__(self, get_url, test_url='http://www.xbiquge.la/0/419/', proxy_name=None, txt_split=None, proxy_port=None):
        self.get_url = get_url
        self.test_url = test_url
        self.proxy_name = proxy_name
        self.txt_split = txt_split
        self.proxy_port = proxy_port
        self.proxy = 'http://{}'
        self.session = requests.session()

    def store(self, storeredis=True):
        if storeredis:
            self.store_redis()
        else:
            self.store_txt()

    def store_redis(self):
        pass

    def store_txt(self, filename, useful_list):
        if not filename.endswith('.txt'):
            raise Exception('must be txt filename')
        with open(filename, 'w') as f:
            for ip in useful_list:
                f.write(ip + '\r\n')

    def get_useful_proxy(self):
        useful_list = []
        proxygetter = ProxyGetter(self.get_url,self.session,proxy_name= self.proxy_name,txt_split= self.txt_split,proxy_port= self.proxy_port)
        reslist = proxygetter.get()
        for py in reslist:
            proxy = self.check(py)
            if proxy:
                useful_list.append(py)
        return useful_list

    def check(self, proxy):
        try:
            res = self.session.get(self.test_url, proxies={'http': self.proxy.format(proxy)},timeout=2)
            # print('ccccccckkkkkkkkkkk')
            if res.status_code == 200:
                return proxy
        except Exception as e:
            print(e)
            return None

    def get_fromtxt(self, filename):
        ip_list = []
        with open(filename, 'r') as f:
            for line in f.readlines():
                ip_list.append(line.strip())
        return ip_list


if __name__ == '__main__':
    proxy = Proxyer('http://127.0.0.1:5000/get_all/',proxy_name='proxy')
    a=proxy.get_useful_proxy()
    print(a)
