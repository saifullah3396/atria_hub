from gotrue.types import User

from atria_hub.api.base import BaseApi
from atria_hub.models import AuthLoginModel
from atria_hub.utilities import get_logger

logger = get_logger(__name__)


class AuthApi(BaseApi):
    @property
    def user(self) -> User:
        """Return the user ID from the Supabase session."""
        session = self.get_session()
        if not session:
            raise RuntimeError("No active session. Please authenticate.")
        return session.user

    def get_session(self):
        try:
            return self._client.auth_client.auth.get_session()
        except Exception:
            return None

    def initialize_auth(
        self, credentials: AuthLoginModel | None = None, force_sign_in: bool = False
    ):
        """Authenticate user and store the session."""
        session = self.get_session()
        if not session or force_sign_in:
            if credentials is None:
                email = input("Enter your email: ")
                password = input("Enter your password: ")
                credentials = AuthLoginModel(email=email, password=password)

            self.sign_in(credentials=credentials)

    def sign_in(self, credentials: AuthLoginModel | None = None):
        """Sign in the user."""
        try:
            result = self._client.auth_client.auth.sign_in_with_password(
                credentials.model_dump()
            )
            if not result.session or not result.user:
                raise RuntimeError("Sign-in failed. Please check your credentials.")
            logger.info(f"Sign-in successful for {credentials.email}")
        except Exception as e:
            logger.error(f"Failed to sign in: {e}")

    def sign_up(
        self, email: str, password: str, username: str, full_name: str | None = None
    ):
        """Sign up a new user."""
        try:
            result = self._client.auth_client.auth.sign_up(
                {
                    "email": email,
                    "password": password,
                    "options": {"data": {"username": username, "full_name": full_name}},
                }
            )
            if not result.session or not result.user:
                raise RuntimeError("Sign-up failed. Please check your credentials.")
            logger.info(f"Sign-up successful for {email}")
        except Exception as e:
            logger.error(f"Failed to sign up: {e}")

    def sign_out(self):
        """Sign out the user by removing the session."""
        try:
            self._client.auth_client.auth.sign_out()
            logger.info("Signed out successfully")
        except Exception as e:
            logger.error(f"Failed to sign out: {e}")
