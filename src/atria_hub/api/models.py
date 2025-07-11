from typing import Optional

import tqdm
from atriax_client.models.body_model_create import BodyModelCreate
from atriax_client.models.data_instance_type import DataInstanceType
from atriax_client.models.model import Model

from atria_hub.api.base import BaseApi


class ModelsApi(BaseApi):
    def get(self, name: str):
        """Retrieve a model from the hub by its name."""
        from atriax_client.api.model import model_find_one

        with self._client.api_client as client:
            response = model_find_one.sync_detailed(client=client, name=name)
            if response.status_code != 200:
                raise RuntimeError(
                    f"Failed to create model: {response.status_code} - {response.content.decode('utf-8')}"
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
        name: str,
        description: str | None = None,
        data_instance_type: Optional["DataInstanceType"] = None,
        is_public: bool = False,
    ) -> Model:
        """Get or create a model in the hub."""
        try:
            return self.get(name=name)
        except Exception:
            return self.create(
                body=BodyModelCreate(
                    name=name,
                    description=description,
                    data_instance_type=data_instance_type,
                    is_public=is_public,
                )
            )

    def upload_files(
        self, model: Model, branch: str, model_files: list[tuple[str, str]]
    ) -> "Model":
        # iterate over the model files and upload them to the hub
        for file in tqdm.tqdm(model_files, desc="Uploading model files to hub"):
            src, tgt = file

            # this is slow but for now it works, in future we could use s3 gateway with async boto3 client instead
            self._client.fs.put_file(lpath=src, rpath=f"{model.repo_id}/{branch}/{tgt}")
