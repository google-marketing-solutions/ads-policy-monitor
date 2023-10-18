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
"""Utilities for working with the Google Ads API."""
import logging
import os
import sys
from typing import List

from gaarf.api_clients import GoogleAdsApiClient
from gaarf.builtin_queries import BUILTIN_QUERIES
from gaarf.io import reader
from gaarf.query_executor import AdsReportFetcher
from gaarf.report import GaarfReport

import models
import utils

logging.basicConfig(stream=sys.stdout)
logger = logging.getLogger(__name__)
logger.setLevel(logging.INFO)

GOOGLE_ADS_API_VERSION = 'v14'

GOOGLE_ADS_REFRESH_TOKEN = os.environ.get('GOOGLE_ADS_REFRESH_TOKEN')
GOOGLE_ADS_CLIENT_ID = os.environ.get('GOOGLE_ADS_CLIENT_ID')
GOOGLE_ADS_CLIENT_SECRET = os.environ.get('GOOGLE_ADS_CLIENT_SECRET')
GOOGLE_ADS_DEVELOPER_TOKEN = os.environ.get('GOOGLE_ADS_DEVELOPER_TOKEN')


def get_ads_client(payload: models.Payload) -> GoogleAdsApiClient:
    """Get a Google Ads Client based on the payload.

    Args:
        payload: the configuration used in this execution.

    Returns:
        The GAARF implementation of the Google Ads API client
    """
    logger.info('Getting Google Ads client.')
    credentials = {
        'developer_token': GOOGLE_ADS_DEVELOPER_TOKEN,
        'refresh_token': GOOGLE_ADS_REFRESH_TOKEN,
        'client_id': GOOGLE_ADS_CLIENT_ID,
        'client_secret': GOOGLE_ADS_CLIENT_SECRET,
        'use_proto_plus': True,
        'login_customer_id': payload.google_ads_login_customer_id,
    }
    return GoogleAdsApiClient(config_dict=credentials,
                              version=GOOGLE_ADS_API_VERSION)


def run_gaarf_report(payload: models.Payload,
                     report_type: models.ReportType,
                     report_fetcher: AdsReportFetcher = None) -> GaarfReport:
    """Run a report through GAARF.

    Args:
        payload: the configuration used in this execution.
        report_type: the report to run.
        report_fetcher: an instance of the AdsReportFetcher for dependency
            injection.

    Returns:
        A GAARF report.

    Raises:
        NotImplementedError if an unexpected report type is provided.
    """
    logger.info('Running report from gaarf for %s:', report_type.value)
    if report_fetcher is None:
        client = get_ads_client(payload)
        report_fetcher = AdsReportFetcher(client)

    if report_type == models.ReportType.OCID:
        return run_builtin_query(query_name='ocid_mapping',
                                 report_fetcher=report_fetcher,
                                 customer_ids=payload.customer_ids)

    if report_type in [models.ReportType.AD_POLICY_DATA]:
        path = f'gaql/{report_type.value.lower()}.sql'
        return run_query_from_file(
            query_path=path,
            report_fetcher=report_fetcher,
            customer_ids=payload.customer_ids,
        )

    raise NotImplementedError(f'{report_type.value} has not been implemented')


def run_builtin_query(query_name: str, report_fetcher: AdsReportFetcher,
                      customer_ids: List[int]) -> GaarfReport:
    """Run a built-in query from GAARF and return the report."""
    logger.info('Running built-in query: %s', query_name)
    return BUILTIN_QUERIES[query_name](report_fetcher, customer_ids)


def run_query_from_file(query_path: str, report_fetcher: AdsReportFetcher,
                        customer_ids: List[int]) -> GaarfReport:
    """Run a query from a file and return the report."""
    logger.info('Running query for: %s', query_path)
    reader_client = reader.FileReader()
    query = reader_client.read(query_path)
    # replace special today placeholder with the correct date
    query = query.replace('{{ today }}', f'"{utils.get_current_date()}"')
    logger.info(query)
    return report_fetcher.fetch(query, customer_ids)
