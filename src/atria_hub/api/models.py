from __future__ import annotations

from typing import TYPE_CHECKING

from atria_hub.api.base import BaseApi

if TYPE_CHECKING:
    import uuid

    import yaml
    from atriax_client.models.body_model_create import BodyModelCreate
    from atriax_client.models.model import Model
    from atriax_client.models.task_type import TaskType


class ModelsApi(BaseApi):
    def get(self, id: uuid.UUID) -> Model:
        """Retrieve a model from the hub by its name."""

        from atriax_client.api.model import model_item

        with self._client.protected_api_client as client:
            response = model_item.sync_detailed(id, client=client)
            if response.status_code != 200:
                raise RuntimeError(
                    f"Failed to get model: {response.status_code} - {response.content.decode('utf-8')}"
                )
            return response.parsed

    def get_by_name(self, username: str, name: str):
        """Retrieve a model from the hub by its name."""

        from atriax_client.api.model import model_find_one

        with self._client.protected_api_client as client:
            response = model_find_one.sync_detailed(
                client=client, username=username, name=name
            )
            if response.status_code != 200:
                raise RuntimeError(
                    f"Failed to get model: {response.status_code} - {response.content.decode('utf-8')}"
                )
            return response.parsed

    def create(self, body: BodyModelCreate):
        """Create a new model in the hub."""

        from atriax_client.api.model import model_create

        with self._client.protected_api_client as client:
            response = model_create.sync_detailed(client=client, body=body)
            if response.status_code != 200:
                raise RuntimeError(
                    f"Failed to create model: {response.status_code} - {response.content.decode('utf-8')}"
                )
            return response.parsed

    def get_or_create(
        self,
        username: str,
        name: str,
        task_type: TaskType,
        description: str | None = None,
        is_public: bool = False,
    ) -> Model:
        """Get or create a model in the hub."""

        from atriax_client.models.body_model_create import BodyModelCreate

        try:
            return self.get_by_name(username=username, name=name)
        except Exception:
            return self.create(
                body=BodyModelCreate(
                    name=name,
                    task_type=task_type,
                    description=description,
                    is_public=is_public,
                )
            )

    def upload_checkpoint(
        self, model: Model, branch: str, model_checkpoint: bytes, model_config: dict
    ) -> Model:
        import lakefs

        branch: lakefs.Branch = lakefs.repository(
            model.repo_id, client=self._client.lakefs_client
        ).branch(branch)
        branch.create(model.default_branch, exist_ok=True)
        branch.object("model.pt").upload(model_checkpoint)
        branch.object("conf/model/config.yaml").upload(
            yaml.dump(model_config).encode("utf-8")
        )

    def load_checkpoint_and_config(
        self, model_repo_id: str, branch: str
    ) -> tuple[bytes, dict]:
        import lakefs

        """Download files from a model."""
        branch: lakefs.Branch = lakefs.repository(
            model_repo_id, client=self._client.lakefs_client
        ).branch(branch)
        with branch.object("model.pt").reader(pre_sign=True) as f:
            model = f.read()
        with branch.object("conf/model/config.yaml").reader(pre_sign=True) as f:
            config = yaml.safe_load(f.read().decode("utf-8"))
        if not isinstance(config, dict):
            raise ValueError(
                "The model configuration is not a valid dictionary. "
                "Please ensure the model was saved with the configuration."
            )
        return model, config
