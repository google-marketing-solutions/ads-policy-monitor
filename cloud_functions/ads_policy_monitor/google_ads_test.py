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
"""Unit tests for google_ads.py"""
import random
import unittest
from unittest.mock import MagicMock, patch
import google_ads
import models


class GoogleAdsTestCase(unittest.TestCase):

    def setUp(self) -> None:
        self.mock_payload = MagicMock()
        self.mock_payload.use_synthetic_data = False
        self.mock_report_fetcher = MagicMock()
        self.ocid_report_config = models.ReportConfig(
            table_name='Ocid',
            write_disposition='WRITE_TRUNCATE',
            is_builtin=True,
            builtin_query_name='ocid_mapping')
        self.ad_policy_data_config = models.ReportConfig(
            table_name='AdPolicyData',
            write_disposition='WRITE_APPEND',
            is_builtin=False,
            gaql_filename='ad_policy_data.sql')

    @patch('google_ads.run_builtin_query')
    def test_run_gaarf_report_with_ocid(self, mock_run_builtin_query):
        google_ads.run_gaarf_report(self.mock_payload, self.ocid_report_config,
                                    self.mock_report_fetcher)
        mock_run_builtin_query.assert_called_with(
            query_name=self.ocid_report_config.builtin_query_name,
            report_fetcher=self.mock_report_fetcher,
            customer_ids=self.mock_payload.customer_ids,
        )

    @patch('google_ads.get_google_ads_synthetic_data')
    def test_run_gaarf_report_for_synthetic_data(
            self, mock_get_google_ads_synthetic_data):
        self.mock_payload.use_synthetic_data = True
        google_ads.run_gaarf_report(self.mock_payload, self.ocid_report_config,
                                    self.mock_report_fetcher)
        mock_get_google_ads_synthetic_data.assert_called_with(table_name='Ocid')

    @patch('google_ads.run_query_from_file')
    def test_run_gaarf_report_with_ad_policy_data(self,
                                                  mock_run_query_from_file):
        google_ads.run_gaarf_report(self.mock_payload,
                                    self.ad_policy_data_config,
                                    self.mock_report_fetcher)
        mock_run_query_from_file.assert_called_once()

    def test_get_google_ads_synthetic_data_ocid(self):
        report = google_ads.get_google_ads_synthetic_data('Ocid')
        self.assertTrue(len(report.column_names), 2)
        self.assertEqual(report.column_names, ['account_id', 'ocid'])
        self.assertTrue(len(report.results), 3)

    @patch('google_ads.utils')
    def test_get_google_ads_synthetic_data_ad_policy_data(self, mock_utils):
        mock_utils.get_current_date.return_value = '2024-01-01'
        random.seed(1)
        report = google_ads.get_google_ads_synthetic_data('AdPolicyData')
        self.assertTrue(len(report.column_names), 17)
        self.assertEqual(report.results[0][0], '2024-01-01')
        self.assertTrue(len(report.results), 998)

    def test_get_google_ads_synthetic_data_missing(self):
        with self.assertRaises(FileNotFoundError):
            google_ads.get_google_ads_synthetic_data('MissingData')


if __name__ == '__main__':
    unittest.main()
