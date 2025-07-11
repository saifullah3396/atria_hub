import keyring
from gotrue._sync.storage import SyncSupportedStorage

from atria_hub.utilities import get_logger

logger = get_logger(__name__)


class CredentialsStorage(SyncSupportedStorage):
    def __init__(self, service_name: str):
        self._service_name = service_name

    def get_item(self, key: str) -> str | None:
        """Retrieve an item from keyring storage asynchronously."""
        try:
            return keyring.get_password(self._service_name, key)
        except Exception as e:
            logger.error(f"Failed to get item from keyring: {e}")
            return None

    def set_item(self, key: str, value: str) -> None:
        """Set an item in keyring storage asynchronously."""
        try:
            keyring.set_password(self._service_name, key, value)
        except Exception as e:
            logger.error(f"Failed to set item in keyring: {e}")

    def remove_item(self, key: str) -> None:
        """Remove an item from keyring storage asynchronously."""
        try:
            if keyring.get_password(self._service_name, key) is not None:
                keyring.delete_password(self._service_name, key)
        except Exception as e:
            logger.error(f"Failed to remove item from keyring: {e}")
