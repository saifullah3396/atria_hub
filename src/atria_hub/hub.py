from __future__ import annotations

from typing import TYPE_CHECKING

from atria_hub.config import settings
from atria_hub.models import AuthLoginModel
from atria_hub.utilities import get_logger

if TYPE_CHECKING:
    from atria_hub.api.auth import AuthApi
    from atria_hub.api.datasets import DatasetsApi
    from atria_hub.api.health_check import HealthCheckApi
    from atria_hub.api.models import ModelsApi
    from atria_hub.client import AtriaHubClient

logger = get_logger(__name__)


class AtriaHub:
    def __init__(
        self,
        base_url: str = settings.ATRIAX_URL,
        storage_url: str = settings.ATRIAX_STORAGE_URL,
        anon_api_key: str = settings.ATRIAX_ANON_KEY,
        service_name: str = "atria",
        use_key_ring: bool = True,
    ):
        from atria_hub.api.auth import AuthApi
        from atria_hub.api.credentials import RepoCredentialsApi
        from atria_hub.api.datasets import DatasetsApi
        from atria_hub.api.health_check import HealthCheckApi
        from atria_hub.api.models import ModelsApi
        from atria_hub.client import AtriaHubClient

        self._base_url = base_url
        self._storage_url = storage_url
        self._client = AtriaHubClient(
            base_url=base_url,
            storage_url=storage_url,
            anon_api_key=anon_api_key,
            service_name=service_name,
            use_key_ring=use_key_ring,
        )

        # initialize apis
        ## health check api
        self._health_check_api = HealthCheckApi(client=self._client)
        self._health_check_api.health_check()

        ## auth api
        self._auth_api = AuthApi(client=self._client)

        ## initialize datasets repo api
        self._datasets = DatasetsApi(client=self._client)
        self._models = ModelsApi(client=self._client)

        ## initialize repo credentials api
        self._repo_credentials = RepoCredentialsApi(client=self._client)

    def initialize(
        self, credentials: AuthLoginModel | None = None, force_sign_in: bool = False
    ) -> "AtriaHub":
        """Initialize the AtriaHub client and authenticate."""
        try:
            self._health_check_api.health_check()
        except RuntimeError:
            logger.error("AtriaHub is unreachable. Please check your connection.")
            raise
        self._auth_api.initialize_auth(
            email=credentials.email if credentials is not None else None,
            password=credentials.password if credentials is not None else None,
            force_sign_in=force_sign_in,
        )
        self._client.set_auth_headers(self.get_auth_headers())
        self._storage_credentials = self._repo_credentials.get_or_create()
        self._client.set_repos_access_credentials(self._storage_credentials)
        return self

    def get_storage_options(self) -> dict[str, str]:
        return {
            "AWS_ACCESS_KEY_ID": self._storage_credentials.access_key_id,
            "AWS_SECRET_ACCESS_KEY": self._storage_credentials.secret_access_key,
            "AWS_ENDPOINT": self._storage_url,
            "AWS_REGION": "stub",
            "AWS_ALLOW_HTTP": "true",
            "AWS_S3_ALLOW_UNSAFE_RENAME": "true",
        }

    def get_auth_headers(self) -> dict[str, str]:
        """Return headers using the Supabase session token."""
        session = self._auth_api.get_session()
        if not session:
            raise RuntimeError("No active session. Please authenticate.")
        return {"Authorization": f"Bearer {session.access_token}"}

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
