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
"""Helpful functions"""
from datetime import datetime
import json
from typing import Dict
from models import ReportConfig


def get_current_date():
    current_date = datetime.now()
    # Format the returned date as 'YYYY-MM-DD'
    return current_date.strftime('%Y-%m-%d')


def load_report_configs(
        filename: str = 'config.json') -> Dict[str, ReportConfig]:
    """Load the reports based on the json configuration file.

    Params:
        filename: the name of the json config file

    Returns:
        A dictionary with keys containing the table_name, and the value the
        ReportConfig. For example:

        {
           AdPolicyData: ReportConfig for AdPolicyData,
        }
    """
    reports_dict = {}
    with open(filename, 'r') as f:
        raw_config = json.load(f)
    for report in raw_config['reports']:
        reports_dict[report['table_name']] = ReportConfig(**report)
    return reports_dict
