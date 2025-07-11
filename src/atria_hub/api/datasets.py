from typing import Optional

import tqdm
from atriax_client.models.body_dataset_create import BodyDatasetCreate
from atriax_client.models.data_instance_type import DataInstanceType
from atriax_client.models.dataset import Dataset

from atria_hub.api.base import BaseApi


class DatasetsApi(BaseApi):
    def get(self, name: str):
        """Retrieve a dataset from the hub by its name."""
        from atriax_client.api.dataset import dataset_find_one

        with self._client.api_client as client:
            response = dataset_find_one.sync_detailed(client=client, name=name)
            if response.status_code != 200:
                raise RuntimeError(
                    f"Failed to create dataset: {response.status_code} - {response.content.decode('utf-8')}"
                )
            return response.parsed

    def create(self, body: BodyDatasetCreate):
        """Create a new dataset in the hub."""
        from atriax_client.api.dataset import dataset_create

        with self._client.protected_api_client as client:
            response = dataset_create.sync_detailed(client=client, body=body)
            if response.status_code != 200:
                raise RuntimeError(
                    f"Failed to create dataset: {response.status_code} - {response.content.decode('utf-8')}"
                )
            return response.parsed

    def get_or_create(
        self,
        name: str,
        description: str | None = None,
        data_instance_type: Optional["DataInstanceType"] = None,
        is_public: bool = False,
    ) -> Dataset:
        """Get or create a dataset in the hub."""
        try:
            return self.get(name=name)
        except Exception:
            return self.create(
                body=BodyDatasetCreate(
                    name=name,
                    description=description,
                    data_instance_type=data_instance_type,
                    is_public=is_public,
                )
            )

    def upload_files(
        self, dataset: Dataset, branch: str, dataset_files: list[tuple[str, str]]
    ) -> "Dataset":
        # iterate over the dataset files and upload them to the hub
        for file in tqdm.tqdm(dataset_files, desc="Uploading dataset files to hub"):
            src, tgt = file

            # this is slow but for now it works, in future we could use s3 gateway with async boto3 client instead
            tgt = f"{dataset.repo_id}/{branch}/{tgt}"
            self._client.fs.put_file(lpath=src, rpath=tgt)

    def download_files(
        self, dataset: Dataset, branch: str, destination_path: str
    ) -> None:
        """Download files from a dataset."""
        src = f"{dataset.repo_id}/{branch}/"
        tgt = destination_path
        self._client.fs.get(src, tgt, recursive=True)
