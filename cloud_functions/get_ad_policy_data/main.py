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
"""Pull all ads from Google Ads with their approval info and output to Bigquery.

The gaql.sql file contains the query pulled from Google Ads. More info about
this can be found in the docs.
https://developers.google.com/google-ads/api/fields/v12/ad_group_ad_query_builder

This data is pulled and output to the specified BigQuery table.
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

logging.basicConfig(stream=sys.stdout)
logger = logging.getLogger(__name__)
logger.setLevel(logging.INFO)

# For local deployment create a flag for the json config file
parser = argparse.ArgumentParser()
parser.add_argument('config_file', type=argparse.FileType('r'))

# The schema of the JSON request
request_schema = {
    'type':
        'object',
    'properties': {
        'bq_output_project': {
            'type': 'string'
        },
        'bq_output_dataset': {
            'type': 'string'
        },
        'bq_output_table': {
            'type': 'string'
        },
        'developer_token': {
            'type': 'string'
        },
        'refresh_token': {
            'type': 'string'
        },
        'client_id': {
            'type': 'string'
        },
        'client_secret': {
            'type': 'string'
        },
        'login_customer_id': {
            'type': 'number'
        },
        'customer_ids': {
            'type': 'array'
        },
    },
    'required': [
        'bq_output_project',
        'bq_output_dataset',
        'bq_output_table',
        'developer_token',
        'refresh_token',
        'client_id',
        'client_secret',
        'login_customer_id',
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
    logger.info('Triggered PolicyMonitor service.')
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

    config = models.Config(**request_json)
    run(config)

    response['status'] = 'Success'
    response['message'] = 'Execution ran successfully'
    return flask.Response(flask.json.dumps(response),
                          status=200,
                          mimetype='application/json')


def run(config: models.Config):
    """The orchestration for the function.

    Args:
        config: the configuration used in this execution.
    """
    logger.info('Running the orchestration for config:')
    logger.info(config)
    ads_data_df = google_ads.get_ad_policy_data(config)
    logger.info('Found %i rows of data', len(ads_data_df))
    bigquery.write_output_dataframe(config, ads_data_df)
    logger.info('Done.')


if __name__ == '__main__':
    args = parser.parse_args()
    with args.config_file as f:
        json_config = json.load(f)
        run(models.Config(**json_config))
