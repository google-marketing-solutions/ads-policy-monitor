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
"""Unit tests for utils.py"""
import unittest
import utils


class UtilsTestCase(unittest.TestCase):

    def test_load_report_configs(self):
        response = utils.load_report_configs()
        self.assertEqual(len(response.keys()), 3)
        self.assertIsNotNone(response.get('Ocid'))
        self.assertIsNotNone(response.get('AdPolicyData'))
        self.assertIsNotNone(response.get('AssetPolicyData'))


if __name__ == '__main__':
    unittest.main()
