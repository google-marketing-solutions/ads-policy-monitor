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
from unittest.mock import MagicMock, patch
import pandas as pd
import bigquery


class BigQueryTestCase(unittest.TestCase):

    @patch('bigquery.pandas_gbq.to_gbq')
    def test_write_output_dataframe(self, mock_pandas_gbq):
        mock_df = pd.DataFrame([{
            'col_a': 1,
            'col_b': 2,
        }])
        mock_config = MagicMock()
        bigquery.write_output_dataframe(config=mock_config, output_df=mock_df)
        mock_pandas_gbq.assert_called_once()


if __name__ == '__main__':
    unittest.main()
