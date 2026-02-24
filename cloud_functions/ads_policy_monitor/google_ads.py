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
import random
import sys
from typing import List, Dict

from gaarf.api_clients import GoogleAdsApiClient
from gaarf.builtin_queries import BUILTIN_QUERIES
from gaarf.io import reader
from gaarf.report_fetcher import AdsReportFetcher
from gaarf.report import GaarfReport
import numpy as np
import pandas as pd

import models
import utils

logging.basicConfig(stream=sys.stdout)
logger = logging.getLogger(__name__)
logger.setLevel(logging.INFO)

GOOGLE_ADS_API_VERSION = 'v23'

GOOGLE_ADS_REFRESH_TOKEN = os.environ.get('GOOGLE_ADS_REFRESH_TOKEN')
GOOGLE_ADS_CLIENT_ID = os.environ.get('GOOGLE_ADS_CLIENT_ID')
GOOGLE_ADS_CLIENT_SECRET = os.environ.get('GOOGLE_ADS_CLIENT_SECRET')
GOOGLE_ADS_DEVELOPER_TOKEN = os.environ.get('GOOGLE_ADS_DEVELOPER_TOKEN')

TIME_SERIES_DATE_COLUMN = "event_date"

GROUP_BY_ASSET_POLICY_COLUMNS = [
    TIME_SERIES_DATE_COLUMN,
    "customer_id",
    "customer_descriptive_name",
    "asset_id",
    "asset_source",
    "asset_type",
    "asset_policy_summary_review_status",
    "asset_policy_summary_policy_topic_entries_topics",
    "asset_policy_summary_approval_status",
    "asset_level",
]


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
                     report_config: models.ReportConfig,
                     report_fetcher: AdsReportFetcher = None) -> GaarfReport:
    """Run a report through GAARF.

    Args:
        payload: the configuration used in this execution.
        report_config: the config of the report to run.
        report_fetcher: an instance of the AdsReportFetcher for dependency
            injection.

    Returns:
        A GAARF report.

    Raises:
        NotImplementedError if an unexpected report type is provided.
    """
    logger.info('Running report from gaarf for %s:', report_config.table_name)

    if payload.use_synthetic_data:
        return get_google_ads_synthetic_data(
            table_name=report_config.table_name)

    if report_fetcher is None:
        client = get_ads_client(payload)
        report_fetcher = AdsReportFetcher(client)

    if report_config.is_builtin:
        return run_builtin_query(query_name=report_config.builtin_query_name,
                                 report_fetcher=report_fetcher,
                                 customer_ids=payload.customer_ids)

    if report_config.is_asset_report:
        all_reports = []
        for gaql_filename in report_config.gaql_filenames:
            path = f'gaql/{gaql_filename}'
            all_reports.append(
                run_query_from_file(
                    query_path=path,
                    report_fetcher=report_fetcher,
                    customer_ids=payload.customer_ids,
                ))
        return combine_assets_reports(all_reports)

    path = f'gaql/{report_config.gaql_filenames}'
    return run_query_from_file(
        query_path=path,
        report_fetcher=report_fetcher,
        customer_ids=payload.customer_ids,
    )


def combine_assets_reports(gaarf_reports: List[GaarfReport]) -> GaarfReport:
    """Combine assets reports.

    Args:
        gaarf_reports: a list of gaarf reports.

    Returns:
        A GAARF report.
    """
    logger.info('Combining Assets reports')
    combined_assets_report = pd.DataFrame()
    for report in gaarf_reports:
        report_df = report.to_pandas()

        # If no results in the report, then skip
        if report_df.empty or report_df["customer_id"][0] == 0:
            continue

        if ("ad_group_id" in report_df.keys() and
                "campaign_id" in report_df.keys()):
            report_df["asset_level"] = "Ad Group"
        elif ("campaign_id" in report_df.keys()):
            report_df["asset_level"] = "Campaign"
            report_df["ad_group_id"] = None
        else:
            report_df["asset_level"] = "Account"
            report_df["ad_group_id"] = None
            report_df["campaign_id"] = None

        # Convert policy_topic_entries to str (otherwise group by will fail)
        report_df[
            "asset_policy_summary_policy_topic_entries_topics"] = report_df[
                "asset_policy_summary_policy_topic_entries_topics"].apply(
                    lambda x: x if isinstance(x, str) else ' | '.join(x))

        # Get number of times the asset is used per level, and example IDs it is used at
        report_df = report_df.groupby(GROUP_BY_ASSET_POLICY_COLUMNS).agg(
            example_campaign_id=('campaign_id', 'first'),
            example_ad_group_id=('ad_group_id', 'first'),
            counts=('asset_id', 'count')).reset_index()

        combined_assets_report = pd.concat([combined_assets_report, report_df])

    if ('example_campaign_id' in combined_assets_report.keys() or
            'example_ad_group_id' in combined_assets_report.keys()):
        combined_assets_report['example_campaign_id'] = combined_assets_report[
            'example_campaign_id'].fillna(0)
        combined_assets_report['example_ad_group_id'] = combined_assets_report[
            'example_ad_group_id'].fillna(0)

    return GaarfReport.from_pandas(combined_assets_report)


def extract_time_series(gaarf_report: GaarfReport,
                        report_config: models.ReportConfig) -> GaarfReport:
    """Creates time series report from a gaarf report

    Args:
        gaarf_report: a gaarf report.
        report_config: the config of the report to run.

    Returns:
        A GAARF report.
    """
    logger.info('Creating time series')
    report_df = gaarf_report.to_pandas()
    report_df = report_df.groupby([
        TIME_SERIES_DATE_COLUMN, report_config.time_series_variable_column
    ]).size().reset_index(name='counts')

    return GaarfReport.from_pandas(report_df)


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


def get_google_ads_synthetic_data(table_name: str) -> GaarfReport:
    """Read in the synthetic data based on the table name of the report."""
    logger.info('Fetching synthetic data for: %s', table_name)
    df = pd.read_csv(f'synthetic_data/{table_name}.csv')
    if table_name in ['AdPolicyData', 'AssetPolicyData']:
        df['event_date'] = utils.get_current_date()
        # Randomly drop a small subset of rows to add some variance to the time
        # series.
        perc_to_drop = random.randrange(1, 5) / 100
        num_rows_to_drop = int(perc_to_drop * len(df))
        random_indices = np.random.choice(df.index,
                                          num_rows_to_drop,
                                          replace=False)
        df = df.drop(random_indices)
    return GaarfReport.from_pandas(df)
