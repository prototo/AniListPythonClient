import yaml
import json
import requests
from time import time

class AniListClient:

    base_path = 'https://anilist.co/api'
    schema = {}
    session = None
    auth_expires = 0

    client_id = ''
    client_secret = ''

    def __init__(self):
        schema = None
        with open('schema.yml') as f:
            schema = f.read()
        self.schema = yaml.load(schema)

        self.session = requests.Session()
        self.update_auth()

    def update_auth(self):
        res = self.auth_accessToken({
            'grant_type':       'client_credentials',
            'client_id':        self.client_id,
            'client_secret':    self.client_secret
        })

        try:
            body = json.loads(res.text)
            self.session.headers.update({
                'access_token': body.get('access_token', '')
            })
            self.auth_expires = int(body.get('expires', 0))
        except:
            # actually do something here
            print('something bad happened')
            pass

    def form_url(self, signature, data):
        method = signature.get('method', 'get').lower()
        path = signature.get('path', '')

        for param in signature.get('url_params', []):
            path = '/'.join((path, data.get(param, '')))

        if method == 'get':
            pass

        return '/'.join((self.base_path, path))

    """
        MAGIC!
    """
    def __getattr__(self, item):
        parts = item.split('_')
        signature = self.schema

        for part in parts:
            if not signature:
                return None
            if part in signature:
                signature = signature.get(part, None)

        def api_call(data={}):
            if self.auth_expires <= int(time()):
                # self.update_auth()
                pass

            method = signature.get('method', 'get').lower()
            request = self.session.__getattribute__(method)
            if not request:
                # throw bad method in schema
                return False

            url = self.form_url(signature, data)
            body = {key: data.get(key, False) for key in signature.get('body', [])}

            res = request(url, data=body)
            return res

        return api_call
