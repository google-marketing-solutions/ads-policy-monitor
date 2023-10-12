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
import unittest
from unittest.mock import MagicMock, patch
import google_ads
import models


class GoogleAdsTestCase(unittest.TestCase):

    def setUp(self) -> None:
        self.mock_payload = MagicMock()
        self.mock_report_fetcher = MagicMock()

    @patch('google_ads.run_builtin_query')
    def test_run_gaarf_report_with_ocid(self, mock_run_builtin_query):
        google_ads.run_gaarf_report(self.mock_payload, models.ReportType.OCID,
                                    self.mock_report_fetcher)
        mock_run_builtin_query.assert_called_with(
            query_name='ocid_mapping',
            report_fetcher=self.mock_report_fetcher,
            customer_ids=self.mock_payload.customer_ids,
        )

    @patch('google_ads.run_query_from_file')
    def test_run_gaarf_report_with_ad_policy_data(self,
                                                  mock_run_query_from_file):
        google_ads.run_gaarf_report(self.mock_payload,
                                    models.ReportType.AD_POLICY_DATA,
                                    self.mock_report_fetcher)
        mock_run_query_from_file.assert_called_once()

    def test_run_gaarf_report_with_not_implmented_report(self):
        mock_report_type = MagicMock()
        mock_report_type.value.return_value = 'TEST_REPORT_TYPE'
        with self.assertRaises(NotImplementedError):
            google_ads.run_gaarf_report(self.mock_payload, mock_report_type,
                                        self.mock_report_fetcher)


if __name__ == '__main__':
    unittest.main()
