
import requests
import json


class RestApi:

    def __init__(self):
        self.ip_address = '127.0.0.1'
        self.port = 5000

    def build_url(self, relative_api):
        return f"http://{self.ip_address}:{self.port}/{relative_api}"

    def get(self, relative_api):
        print(self.build_url(relative_api))
        response = requests.get(self.build_url(relative_api))
        response.raise_for_status()
        if response.status_code in ['200', '204']:
            return response.json()

    def post(self, relative_api, data=None):
        if data is not None:
            return requests.post(self.build_url(relative_api), data, headers={"Content-Type": "application/json",
                                                                              "Accept": "application/json"})
        else:
            return requests.post(self.build_url(relative_api))


