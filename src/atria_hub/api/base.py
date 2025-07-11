from atria_hub.client import AtriaHubClient


class BaseApi:
    def __init__(self, client: AtriaHubClient):
        self._client = client
