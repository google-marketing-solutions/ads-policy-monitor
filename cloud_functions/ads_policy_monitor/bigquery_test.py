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
"""Unit tests for bigquery.py"""
import unittest
from unittest.mock import MagicMock
import bigquery


class BigQueryTestCase(unittest.TestCase):

    def test_write_gaarf_report_to_bigquery(self):
        mock_payload = MagicMock()
        mock_bq_writer = MagicMock()
        mock_gaarf_report = MagicMock()
        bigquery.write_gaarf_report_to_bigquery(mock_payload, mock_gaarf_report,
                                                'table_name', mock_bq_writer)
        mock_bq_writer.write.assert_called_with(mock_gaarf_report,
                                                destination='table_name')


if __name__ == '__main__':
    unittest.main()
