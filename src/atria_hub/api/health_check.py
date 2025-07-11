from atria_hub.api.base import BaseApi
from atria_hub.utilities import get_logger

logger = get_logger(__name__)


class HealthCheckApi(BaseApi):
    def health_check(self):
        """Perform a health check on the backend."""
        from atriax_client.api.health import health_health_check

        with self._client.api_client as client:
            response = health_health_check.sync_detailed(client=client)
            if response.status_code != 200:
                raise RuntimeError(
                    f"Failed to connect to atriax server: {response.status_code} - {response.content}"
                )
            return response.parsed
