# Copyright 2026 Google LLC
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
"""Unit tests for telemetry.py"""
import os
import sys
import unittest
from unittest.mock import MagicMock, patch

import models
import telemetry


def _payload(**kwargs) -> models.Payload:
    config = {
        'project_id': 'my_project',
        'bq_output_dataset': 'my_dataset',
        'region': 'europe-west2',
        'google_ads_login_customer_id': 1234567890,
        'customer_ids': [1111111111, 2222222222],
    }
    config.update(kwargs)
    return models.Payload(**config)


class TelemetryTestCase(unittest.TestCase):

    def setUp(self):
        super().setUp()
        # A fake tadau module keeps the tests hermetic: no event is ever sent.
        self.mock_tadau = MagicMock()
        self.enterContext(patch.dict(sys.modules, {'tadau': self.mock_tadau}))
        self.enterContext(patch.dict(os.environ, clear=False))
        os.environ.pop(telemetry.DISABLE_TELEMETRY_ENV_VAR, None)

    def _sent_events(self):
        send_events = self.mock_tadau.Tadau.return_value.send_events
        send_events.assert_called_once()
        return send_events.call_args.args[0]

    def test_format_customer_id(self):
        self.assertEqual(telemetry.format_customer_id(1234567890),
                         '123-456-7890')
        self.assertEqual(telemetry.format_customer_id(123456789),
                         '012-345-6789')
        self.assertIsNone(telemetry.format_customer_id(0))
        self.assertIsNone(telemetry.format_customer_id(12345678901))

    def test_send_usage_events(self):
        telemetry.send_usage_events(_payload())

        self.mock_tadau.Tadau.assert_called_once_with(
            api_secret=telemetry.API_SECRET,
            measurement_id=telemetry.MEASUREMENT_ID,
            opt_in=True,
            fixed_dimensions={
                'app': 'Ads Policy Monitor',
                'is_agent_event': False,
                'non_personalized_ads': False,
            },
        )
        events = self._sent_events()
        self.assertEqual([e['name'] for e in events],
                         ['SOLUTION_USAGE', 'SOLUTION_USAGE'])
        self.assertEqual([e['th_google_ads_customer_id'] for e in events],
                         ['111-111-1111', '222-222-2222'])
        event_ids = [e['external_event_id'] for e in events]
        self.assertTrue(all(event_ids))
        self.assertEqual(len(set(event_ids)), 2)

    def test_duplicate_customer_ids_are_sent_once(self):
        telemetry.send_usage_events(
            _payload(customer_ids=[1111111111, 1111111111]))

        self.assertEqual(len(self._sent_events()), 1)

    def test_not_sent_when_disabled(self):
        os.environ[telemetry.DISABLE_TELEMETRY_ENV_VAR] = 'true'

        telemetry.send_usage_events(_payload())

        self.mock_tadau.Tadau.assert_not_called()

    def test_sent_when_disable_flag_is_false(self):
        os.environ[telemetry.DISABLE_TELEMETRY_ENV_VAR] = 'false'

        telemetry.send_usage_events(_payload())

        self.assertEqual(len(self._sent_events()), 2)

    def test_not_sent_for_synthetic_data(self):
        telemetry.send_usage_events(_payload(use_synthetic_data=True))

        self.mock_tadau.Tadau.assert_not_called()

    def test_not_sent_without_customer_ids(self):
        telemetry.send_usage_events(_payload(customer_ids=[]))

        self.mock_tadau.Tadau.assert_not_called()

    def test_errors_are_not_raised(self):
        self.mock_tadau.Tadau.return_value.send_events.side_effect = (
            RuntimeError('boom'))

        telemetry.send_usage_events(_payload())

        self.mock_tadau.Tadau.return_value.send_events.assert_called_once()

    def test_missing_library_is_not_raised(self):
        with patch.dict(sys.modules, {'tadau': None}):
            telemetry.send_usage_events(_payload())

        self.mock_tadau.Tadau.assert_not_called()


if __name__ == '__main__':
    unittest.main()
