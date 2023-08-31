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

import pandas as pd
import pandas_gbq

import models

logging.basicConfig(stream=sys.stdout)
logger = logging.getLogger(__name__)
logger.setLevel(logging.INFO)


def write_output_dataframe(config: models.Config,
                           output_df: pd.DataFrame) -> None:
    """Output the dataframe to BigQuery."""
    logger.info('Writing output dataframe to BigQuery.')
    destination_table = f'{config.bq_output_dataset}.{config.bq_output_table}'
    pandas_gbq.to_gbq(output_df,
                      destination_table,
                      project_id=config.bq_output_project,
                      if_exists='append')
