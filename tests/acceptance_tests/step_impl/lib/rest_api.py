
import requests
import json


class RestApi:

    def __init__(self): pass

    @staticmethod
    def build_url(relative_api):
        return f"http://localhost:5000/{relative_api}"

    def get(self, relative_api):
        print(self.build_url(relative_api))
        response = requests.get(self.build_url(relative_api))
        response.raise_for_status()
        if response.status_code in ['200', '204']:
            return response.json()

    def post(self, relative_api, data=None):
        if data is not None:
            return requests.post(self.build_url(relative_api), data)
        else:
            return requests.post(self.build_url(relative_api))


