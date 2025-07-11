from atria_hub.api.auth import AuthApi
from atria_hub.api.credentials import RepoCredentialsApi
from atria_hub.api.datasets import DatasetsApi
from atria_hub.api.health_check import HealthCheckApi
from atria_hub.api.models import ModelsApi
from atria_hub.client import AtriaHubClient
from atria_hub.config import settings
from atria_hub.models import AuthLoginModel
from atria_hub.utilities import get_logger

logger = get_logger(__name__)


class AtriaHub:
    def __init__(
        self,
        base_url: str = settings.ATRIAX_URL,
        anon_api_key: str = settings.ATRIAX_ANON_KEY,
        credentials: AuthLoginModel | None = None,
        force_sign_in: bool = False,
        service_name: str = "atria",
    ):
        self._client = AtriaHubClient(
            base_url=base_url, anon_api_key=anon_api_key, service_name=service_name
        )
        # initialize apis
        ## health check api
        self._health_check_api = HealthCheckApi(client=self._client)
        self._health_check_api.health_check()

        ## auth api
        self._auth_api = AuthApi(client=self._client)
        self._auth_api.initialize_auth(
            credentials=credentials, force_sign_in=force_sign_in
        )

        ## initialize repos api access and authenticate
        self._repo_credentials = RepoCredentialsApi(client=self._client)
        self._client.set_repos_access_credentials(
            self._repo_credentials.get_or_create()
        )

        # initialize datasets repo api
        self._datasets = DatasetsApi(client=self._client)
        self._models = ModelsApi(client=self._client)

    @property
    def client(self) -> AtriaHubClient:
        """Return the AtriaHub client."""
        return self._client

    @property
    def health_check(self) -> HealthCheckApi:
        """Return the health check API."""
        return self._health_check_api

    @property
    def auth(self) -> AuthApi:
        """Return the authentication API."""
        return self._auth_api

    @property
    def datasets(self) -> DatasetsApi:
        """Return the datasets API."""
        return self._datasets

    @property
    def models(self) -> ModelsApi:
        """Return the models API."""
        return self._models
