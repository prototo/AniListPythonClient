import yaml
import json
import requests
from time import time
from schema import Schema

class AniListClient:
    config = {}
    schema = None
    session = None
    auth_expires = 0

    def __init__(self):
        self.schema = Schema()
        self.session = requests.Session()

        self.load_config()
        self.update_auth()

    def load_config(self, config_file='config.yml'):
        with open(config_file) as f:
            self.config = yaml.load(f.read())

    def update_auth(self):
        status, body = self.auth_accessToken({
            'grant_type': 'client_credentials',
            'client_id': self.config['client_id'],
            'client_secret': self.config['client_secret']
        })

        try:
            self.session.headers.update({
                'Authorization': ' '.join(('Bearer', body.get('access_token', '')))
            })
            self.auth_expires = int(body.get('expires', 0))
        except Exception as e:
            # actually do something here
            print(e)

    """
        Proxies to self.send_request

        __getattr__ is called magically when you try to access an attribute not
        explicitly managed by the class. For example, client.anime_search
        will call __getattr__(instance, 'anime_search'), allowing us to build
        an api_call method from the configured schema.
    """
    def __getattr__(self, item):
        return self.send_request(item)

    def send_request(self, signature):
        schema = self.schema.get_schema(signature)

        path = schema.get('path', None)
        method = schema.get('method', 'get').lower()
        params = schema.get('params', [])

        def api_call(data={}):
            if self.auth_expires <= int(time()):
                # self.update_auth()
                pass

            request = self.session.__getattribute__(method)
            if not request:
                # throw bad method in schema
                return False

            # filter out unnecessary pairs in the data dict
            body = {key: data.get(key, False) for key in params}
            res = request(path.format(**data), data=body)
            try:
                return res.status_code, json.loads(res.text)
            except Exception as e:
                return res.status_code, res.text

        return api_call
