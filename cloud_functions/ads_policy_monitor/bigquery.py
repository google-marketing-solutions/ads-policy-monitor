# Copyright 2023 Google LLC
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#     https://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.
"""Utilities for working with the BigQuery."""
import logging
import sys
from gaarf.report import GaarfReport
from gaarf.io import writer
import models

logging.basicConfig(stream=sys.stdout)
logger = logging.getLogger(__name__)
logger.setLevel(logging.INFO)


def write_gaarf_report_to_bigquery(
        payload: models.Payload,
        gaarf_report: GaarfReport,
        report_config: models.ReportConfig,
        table_name: str,
        bq_writer: writer.BigQueryWriter = None) -> None:
    """Output a GAARF report to BigQuery.

    Args:
        payload: the configuration used in this execution.
        gaarf_report: the report to output.
        report_config: the config of the report to run.
        table_name: name of the table to write to.
        bq_writer: for dependency injection, provide a BQ writer class.
    """
    logger.info('Writing report to BigQuery: %s', table_name)
    if bq_writer is None:
        bq_writer = writer.BigQueryWriter(
            project=payload.project_id,
            dataset=payload.bq_output_dataset,
            location=payload.region,
            write_disposition=report_config.write_disposition)

    bq_writer.write(gaarf_report, destination=table_name)
