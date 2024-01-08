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
"""The orchestration for Ads Policy Monitor.

The solution is built around Google Ads API Report Fetcher (GAARF), to simplify
extracting data from the Google Ads API via GAQL.

It pulls data from Google Ads & outputs it to BigQuery.
"""
import argparse
import json
import logging
import sys

import flask
import functions_framework
import jsonschema

import bigquery
import google_ads
import models
import utils

logging.basicConfig(stream=sys.stdout)
logger = logging.getLogger(__name__)
logger.setLevel(logging.INFO)

# For local deployment create a flag for the json config file
parser = argparse.ArgumentParser()
parser.add_argument('payload_file', type=argparse.FileType('r'))

# The schema of the JSON request
request_schema = {
    'type':
        'object',
    'properties': {
        'reports_to_run': {
            'type': 'array'
        },
        'project_id': {
            'type': 'string'
        },
        'bq_output_dataset': {
            'type': 'string'
        },
        'region': {
            'type': 'string'
        },
        'google_ads_login_customer_id': {
            'type': 'number'
        },
        'customer_ids': {
            'type': 'array'
        },
        'use_synthetic_data': {
            'type': 'boolean',
        }
    },
    'required': [
        'project_id',
        'bq_output_dataset',
        'region',
        'google_ads_login_customer_id',
        'customer_ids',
    ]
}


@functions_framework.http
def main(request: flask.Request) -> flask.Response:
    """The entry point: extract the data from the payload and starts the job.

    Args:
        request (flask.Request): The request object.
        <https://flask.palletsprojects.com/en/1.1.x/api/#incoming-request-data>

    Returns:
        The response text, or any set of values that can be turned into a
        Response object using `make_response`
        <https://flask.palletsprojects.com/en/1.1.x/api/#flask.make_response>.
    """
    logger.info('Triggered Ads Policy Monitor service.')
    request_json = request.get_json(silent=True)
    logger.info('JSON payload: %s', request_json)
    response = {}
    try:
        jsonschema.validate(instance=request_json, schema=request_schema)
    except jsonschema.exceptions.ValidationError as err:
        logger.error('Invalid request payload: %s', err)
        response['status'] = 'Failed'
        response['message'] = err.message
        return flask.Response(flask.json.dumps(response),
                              status=400,
                              mimetype='application/json')

    config = models.Payload(**request_json)
    run(config)

    response['status'] = 'Success'
    response['message'] = 'Execution ran successfully'
    return flask.Response(flask.json.dumps(response),
                          status=200,
                          mimetype='application/json')


def run(payload: models.Payload) -> None:
    """The orchestration for the function.

    Args:
        payload: the configuration used in this execution.
    """
    logger.info('Running the orchestration for payload:')
    logger.info(payload)

    report_configs = utils.load_report_configs()
    reports_to_run = payload.reports_to_run or report_configs.keys()

    for report in reports_to_run:
        report_config = report_configs[report]
        gaarf_report = google_ads.run_gaarf_report(payload, report_config)
        if gaarf_report is None:
            logger.warning('GAARF report is None, check configuration.')
            return None
        bigquery.write_gaarf_report_to_bigquery(payload, gaarf_report,
                                                report_config)
    logger.info('Done.')


if __name__ == '__main__':
    args = parser.parse_args()
    with args.payload_file as f:
        json_payload = json.load(f)
        run(models.Payload(**json_payload))
