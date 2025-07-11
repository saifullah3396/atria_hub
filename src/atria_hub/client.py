from atriax_client import Client as AtriaxClient
from lakefs.client import Client as LakeFSClient
from lakefs_spec import LakeFSFileSystem
from supabase import (
    Client as AuthClient,
    Client as SupabaseClient,
    ClientOptions,
    create_client,
)

from atria_hub.config import settings
from atria_hub.credentials_storage import CredentialsStorage
from atria_hub.models import ReposCredentials
from atria_hub.utilities import get_logger

logger = get_logger(__name__)


class AtriaHubClient:
    def __init__(
        self,
        base_url: str = settings.ATRIAX_URL,
        anon_api_key: str = settings.ATRIAX_ANON_KEY,
        service_name: str = "atria",
    ):
        self._base_url = base_url
        self._service_name = service_name
        self._anon_api_key = anon_api_key
        self._credentials_storage = CredentialsStorage(service_name)
        self._api_client = AtriaxClient(base_url=base_url)
        self._auth_client: AuthClient = create_client(
            supabase_url=base_url,
            supabase_key=anon_api_key,
            options=ClientOptions(storage=self._credentials_storage),
        )
        self._repos_client = LakeFSClient(host=self._base_url + "/repos/v1")
        self._repos_client._client._api.set_default_header("apiKey", self._anon_api_key)
        self._lakefs_fs = LakeFSFileSystem(host=self._base_url + "/repos/v1")
        self._lakefs_fs.client = self._repos_client

    @property
    def credentials_storage(self) -> CredentialsStorage:
        """Return the credentials storage."""
        return self._credentials_storage

    @property
    def api_client(self) -> AtriaxClient:
        """Return the HTTP client for REST API calls."""
        return self._api_client.with_headers({"apiKey": self._anon_api_key})

    @property
    def protected_api_client(self) -> AtriaxClient:
        """Return the HTTP client for REST API calls."""
        return self._api_client.with_headers(self._get_auth_headers())

    @property
    def auth_client(self) -> SupabaseClient:
        """Return the Supabase client."""
        return self._auth_client

    @property
    def lakefs_client(self) -> LakeFSClient:
        """Return the LakeFS client."""
        if self._repos_client is None:
            raise RuntimeError("LakeFS client is not initialized.")
        return self._repos_client

    @property
    def fs(self) -> LakeFSFileSystem:
        """Return the LakeFS client."""
        if self._lakefs_fs is None:
            raise RuntimeError("LakeFS client is not initialized.")
        return self._lakefs_fs

    def set_repos_access_credentials(self, credentials: ReposCredentials):
        """Set the credentials in the storage."""
        self._repos_client._conf.username = credentials.access_key_id
        self._repos_client._conf.password = credentials.secret_access_key
