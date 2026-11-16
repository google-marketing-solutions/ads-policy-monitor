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
"""Usage telemetry for Ads Policy Monitor.

Sends a SOLUTION_USAGE event per Google Ads customer ID after a successful run,
using Tadau (https://github.com/google-marketing-solutions/tadau).

Telemetry is fail-open: nothing in this module is allowed to raise or to block
the pipeline for longer than SEND_TIMEOUT_SECONDS.
"""
import logging
import os
import sys
import threading
from typing import List, Optional
import uuid

import models

logging.basicConfig(stream=sys.stdout)
logger = logging.getLogger(__name__)
logger.setLevel(logging.INFO)

APP_NAME = 'Ads Policy Monitor'
EVENT_NAME = 'SOLUTION_USAGE'
MEASUREMENT_ID = 'G-Z2TKLQZ79K'
API_SECRET = 'S7toNnNZQPWzViq44q_8gg'

# Set this environment variable to "true" to stop sending usage telemetry.
DISABLE_TELEMETRY_ENV_VAR = 'ADS_POLICY_MONITOR_DISABLE_TELEMETRY'

# Tadau sends events one by one without a request timeout, so the sending is
# bounded here to make sure telemetry can never hang the function.
SEND_TIMEOUT_SECONDS = 30


def is_enabled() -> bool:
    """Whether usage telemetry should be sent."""
    value = os.environ.get(DISABLE_TELEMETRY_ENV_VAR, '')
    return value.strip().lower() not in ('true', '1', 'yes')


def format_customer_id(customer_id: int) -> Optional[str]:
    """Format a Google Ads customer ID as XXX-XXX-XXXX.

    The hyphens are required: they mark the value as an external customer ID.

    Args:
        customer_id: the Google Ads customer ID, without hyphens.

    Returns:
        The hyphenated customer ID, or None if it is not a valid customer ID.
    """
    digits = str(customer_id).replace('-', '').strip()
    if not digits.isdigit() or len(digits) > 10 or int(digits) == 0:
        return None
    digits = digits.zfill(10)
    return f'{digits[:3]}-{digits[3:6]}-{digits[6:]}'


def build_events(payload: models.Payload) -> List[dict]:
    """Build one SOLUTION_USAGE event per unique customer ID in the payload.

    Args:
        payload: the configuration used in this execution.

    Returns:
        The list of events to send.
    """
    events = []
    seen = set()
    for customer_id in payload.customer_ids:
        formatted_id = format_customer_id(customer_id)
        if formatted_id is None:
            logger.warning('Telemetry: skipping invalid customer ID: %s',
                           customer_id)
            continue
        if formatted_id in seen:
            continue
        seen.add(formatted_id)
        events.append({
            'name': EVENT_NAME,
            'external_event_id': str(uuid.uuid4()),
            'th_google_ads_customer_id': formatted_id,
        })
    return events


def _send(events: List[dict]) -> None:
    """Send the events with Tadau, logging rather than raising any error."""
    try:
        # Imported here so a missing or broken library cannot break the
        # pipeline.
        import tadau  # pylint: disable=import-outside-toplevel

        client = tadau.Tadau(
            api_secret=API_SECRET,
            measurement_id=MEASUREMENT_ID,
            opt_in=True,
            fixed_dimensions={
                'app': APP_NAME,
                'is_agent_event': False,
                'non_personalized_ads': False,
            },
        )
        client.send_events(events)
    except Exception:  # pylint: disable=broad-exception-caught
        logger.warning('Telemetry: failed to send usage events.', exc_info=True)


def send_usage_events(payload: models.Payload) -> None:
    """Send SOLUTION_USAGE events for a successful run. Never raises.

    Nothing is sent when telemetry is disabled or when the run used synthetic
    data, as those runs do not touch real Google Ads accounts.

    Args:
        payload: the configuration used in this execution.
    """
    try:
        if not is_enabled():
            logger.info('Telemetry: disabled, not sending usage events.')
            return
        if payload.use_synthetic_data:
            return
        events = build_events(payload)
        if not events:
            return
        thread = threading.Thread(target=_send, args=(events,), daemon=True)
        thread.start()
        thread.join(timeout=SEND_TIMEOUT_SECONDS)
        if thread.is_alive():
            logger.warning('Telemetry: timed out sending usage events.')
    except Exception:  # pylint: disable=broad-exception-caught
        logger.warning('Telemetry: failed to send usage events.', exc_info=True)
