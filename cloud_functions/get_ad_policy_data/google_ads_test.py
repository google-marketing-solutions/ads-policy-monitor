# Copyright 2022 Google LLC
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
"""Unit tests for main.py"""
import unittest
from unittest.mock import MagicMock, patch
import google_ads
import models


class GoogleAdsTestCase(unittest.TestCase):

    def setUp(self) -> None:
        self.config = models.Config(**{
          'bq_output_project': 'my_project',
          'bq_output_dataset': 'my_dataset',
          'bq_output_table': 'KeywordsWithAccounts',
          'developer_token': 'abc-123',
          'refresh_token': '1//abc123',
          'client_id': 'abc123.apps.googleusercontent.com',
          'client_secret': 'client_secret',
          'login_customer_id': 1234567890,
          'customer_ids': [111122222, 2222223333]
        })

    def test_load_gaql_query(self):
        query = google_ads.load_gaql_query('test_data/gads_test.sql')
        expected_query = (
            'SELECT\n'
            '  customer.id,\n'
            '  customer.descriptive_name\n'
            'FROM\n'
            '  ad_group_ad'
        )
        self.assertEqual(expected_query, query)

    @patch('google_ads.load_gaql_query')
    @patch('google_ads.process_ads_policy_stream')
    def test_get_ad_policy_data(self, mock_stream, mock_load_query):
        mock_client = MagicMock()
        google_ads.get_ad_policy_data(self.config, mock_client)
        mock_load_query.assert_called_once()
        mock_stream.assert_called_once()


if __name__ == '__main__':
    unittest.main()
