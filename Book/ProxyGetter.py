import requests


class ProxyGetter:

    def __init__(self, get_url,session=None, proxy_name=None, txt_split=None,proxy_port=None):
        self.url = get_url
        self.proxy_name = proxy_name
        self.txt_split = txt_split
        self.proxy_port = proxy_port
        self.session = session if session else requests.session()

    def patch(self):
        res = requests.get(self.url)
        try:
            return res.json()
        except Exception:
            return res.text

    def parse(self, response):
        if isinstance(response, dict):
            res_list = self.parse_dict(response)
        elif isinstance(response, list):
            res_list = self.parse_list(response)
            print(res_list)
        else:
            res_list = self.parse_txt(response)
        return res_list

    def parse_dict(self, res_dict) -> list:
        res = []
        proxy = res_dict.get(self.proxy_name)
        if proxy:
            if self.proxy_port:
                proxy += res_dict.get(self.proxy_port)
                res.append(proxy)
                return res
            else:
                res.append(proxy)
                return res
        return res

    def parse_list(self, res_list) -> list:
        res = []
        for ipinfo in res_list[:8]:
            res.extend(self.parse_dict(ipinfo))
        return res

    def parse_txt(self, res_txt) -> list:
        txt_split_list = res_txt.split(self.txt_split)
        return txt_split_list

    def get(self):
        response = self.patch()
        res_list = self.parse(response)
        return res_list