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
from typing import List
"""The pydantic models for the project."""
from pydantic import BaseModel, SecretStr


class Config(BaseModel):
    project_id: str
    bq_output_dataset: str
    bq_output_table: str
    google_ads_developer_token: SecretStr
    oauth_refresh_token: SecretStr
    google_cloud_client_id: str
    google_cloud_client_secret: SecretStr
    google_ads_login_customer_id: int
    customer_ids: List[int]
