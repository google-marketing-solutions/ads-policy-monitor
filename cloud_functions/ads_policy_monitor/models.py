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
"""The pydantic models & constants for the project."""
from typing import List, Optional, Union
from pydantic import BaseModel


class ReportConfig(BaseModel):
    table_name: str
    write_disposition: str
    is_builtin: bool = False
    is_asset_report: bool = False
    builtin_query_name: Optional[str] = None
    gaql_filenames: Optional[Union[str, List[str]]] = None


class Payload(BaseModel):
    reports_to_run: Optional[List[str]] = None
    project_id: str
    bq_output_dataset: str
    region: str
    google_ads_login_customer_id: int
    customer_ids: List[int]
    use_synthetic_data: bool = False
