from __future__ import annotations

import uuid
from typing import TYPE_CHECKING, Any
from uuid import UUID

from atria_core.logger.logger import get_logger

from atria_hub.api.base import BaseApi
from atria_hub.client import AtriaHubClient
from atria_hub.exceptions import api_error_handler

if TYPE_CHECKING:
    from atriax_client.models.model_evaluation import ModelEvaluation

logger = get_logger(__name__)


class EvaluationSampleResultApi(BaseApi):
    @api_error_handler
    def list_indices(self, evaluation_id: UUID) -> list[int]:
        """Read a batch of sample results from an evaluation."""
        from atriax_client.api.sample_results import sample_results_list_indices

        with self._client.protected_api_client as client:
            return sample_results_list_indices.sync_detailed(
                client=client, evaluation_id=evaluation_id
            )

    @api_error_handler
    def write(
        self, evaluation_id: UUID, data_per_sample_index: dict[int, dict]
    ) -> None:
        """Write a sample result to an evaluation."""
        from atriax_client.api.sample_results import sample_results_write
        from atriax_client.models import (
            EvaluationSampleResultCreate,
            EvaluationSampleResultCreateData,
        )

        with self._client.protected_api_client as client:
            return sample_results_write.sync_detailed(
                client=client,
                evaluation_id=evaluation_id,
                body=[
                    EvaluationSampleResultCreate(
                        sample_index=sample_index,
                        data=EvaluationSampleResultCreateData.from_dict(data),
                    )
                    for sample_index, data in data_per_sample_index.items()
                ],
            )

    @api_error_handler
    def read(self, evaluation_id: UUID, sample_indices: list[int]) -> list[dict]:
        """Read a batch of sample results from an evaluation."""
        from atriax_client.api.sample_results import sample_results_read

        with self._client.protected_api_client as client:
            return sample_results_read.sync_detailed(
                client=client, evaluation_id=evaluation_id, body=sample_indices
            )


class EvaluationMetricsApi(BaseApi):
    def __init__(self, client: AtriaHubClient):
        self._client = client

    @api_error_handler
    def write(self, evaluation_id: UUID, metrics: dict[str, Any]) -> None:
        """Write a sample result to an evaluation."""
        from atriax_client.api.metrics import metrics_write
        from atriax_client.models.evaluation_metric_create import EvaluationMetricCreate

        logger.info("metrics %s", metrics)
        with self._client.protected_api_client as client:
            return metrics_write.sync_detailed(
                client=client,
                evaluation_id=evaluation_id,
                body=[
                    EvaluationMetricCreate(key=key, value=value)
                    for key, value in metrics.items()
                ],
            )

    @api_error_handler
    def read(self, evaluation_id: UUID) -> list[dict]:
        """Read a batch of sample results from an evaluation."""
        from atriax_client.api.metrics import metrics_read

        with self._client.protected_api_client as client:
            return metrics_read.sync_detailed(
                client=client, evaluation_id=evaluation_id
            )


class EvaluationsApi(BaseApi):
    def __init__(self, client: AtriaHubClient):
        self._client = client
        self._sample_results = EvaluationSampleResultApi(client)
        self._metrics = EvaluationMetricsApi(client)

    @property
    def sample_results(self) -> EvaluationSampleResultApi:
        """Access to sample results API."""
        return self._sample_results

    @property
    def metrics(self) -> EvaluationMetricsApi:
        """Access to metrics API."""
        return self._metrics

    @api_error_handler
    def get_or_create(
        self,
        dataset_id: UUID,
        dataset_branch: str,
        dataset_config_name: str,
        dataset_split: str,
        model_id: UUID,
        model_branch: str,
        model_config_name: str,
    ) -> ModelEvaluation:
        """Retrieve a dataset from the hub by its name."""

        from atriax_client.api.evaluations import evaluations_get_or_create
        from atriax_client.models.model_evaluation_get_or_create import (
            ModelEvaluationGetOrCreate,
        )

        with self._client.protected_api_client as client:
            return evaluations_get_or_create.sync_detailed(
                client=client,
                body=ModelEvaluationGetOrCreate(
                    dataset_id=dataset_id,
                    dataset_branch=dataset_branch,
                    dataset_config_name=dataset_config_name,
                    dataset_split=dataset_split,
                    model_id=model_id,
                    model_branch=model_branch,
                    model_config_name=model_config_name,
                ),
            )

    @api_error_handler
    def delete(self, id: uuid.UUID) -> None:
        from atriax_client.api.dataset import dataset_delete

        with self._client.protected_api_client as client:
            return dataset_delete.sync_detailed(client=client, id=id)
