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
"""The pydantic models for the project."""
from pydantic import BaseModel, SecretStr


class Config(BaseModel):
    bq_output_project: str
    bq_output_dataset: str
    bq_output_table: str
    developer_token: SecretStr
    refresh_token: SecretStr
    client_id: str
    client_secret: SecretStr
    login_customer_id: int
    customer_id: int
