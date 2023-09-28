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
import sys
from typing import Any, Iterable

from google.ads.googleads.client import GoogleAdsClient
from google.ads.googleads.errors import GoogleAdsException

import pandas as pd
import sqlparse

import models
import utils

logging.basicConfig(stream=sys.stdout)
logger = logging.getLogger(__name__)
logger.setLevel(logging.INFO)


def get_ad_policy_data(config: models.Config,
                       client: GoogleAdsClient = None) -> pd.DataFrame:
    """Get the ad policy data from the Google Ads account.

    Args:
        config: the configuration used in this execution.
        client: optionally provide a Google Ads client.

    Returns:
        A Pandas Dataframe with the results
    """
    logger.info('Getting ad policy data from Google Ads.')

    if client is None:
        client = get_ads_client(config)

    all_policy_data = fetch_data_from_accounts_stream(client,
                                                      config.customer_ids)
    policy_dataframe = process_ads_policy_data(client, all_policy_data)

    return policy_dataframe


def fetch_data_from_accounts_stream(client: GoogleAdsClient, customer_ids):
    all_results = []
    ga_service = client.get_service('GoogleAdsService')

    for customer_id in customer_ids:
        logger.info('Fetching data from Google Ads for customer: ' +
                    str(customer_id))
        try:
            search_request = client.get_type('SearchGoogleAdsStreamRequest')
            search_request.customer_id = str(customer_id)
            query = load_gaql_query()
            search_request.query = query

            stream = ga_service.search_stream(request=search_request)

            for response in stream:
                for row in response.results:
                    all_results.append(row)
        except GoogleAdsException as ex:
            print(f"Error fetching data for customer {customer_id}: {ex}")

    return all_results


def process_ads_policy_data(client: GoogleAdsClient,
                            policy_data: Iterable[Any]) -> pd.DataFrame:
    rows_to_insert = []

    for row in policy_data:
        # logger.info('Row' + str(row))
        policy_summary = row.ad_group_ad.policy_summary

        campaign_status = client.enums.CampaignStatusEnum(
            row.campaign.status).name
        campaign_primary_status = client.enums.CampaignPrimaryStatusEnum(
            row.campaign.primary_status).name
        ad_group_status = client.enums.AdGroupStatusEnum(
            row.ad_group.status).name
        ad_group_ad_status = client.enums.AdGroupAdStatusEnum(
            row.ad_group_ad.status).name
        policy_approval_status = client.enums.PolicyApprovalStatusEnum(
            policy_summary.approval_status).name
        policy_review_status = client.enums.PolicyReviewStatusEnum(
            policy_summary.review_status).name

        for entry in policy_summary.policy_topic_entries or [None]:
            if entry is None:
                policy_type = None
                policy_topic = None
            else:
                policy_type = client.enums.PolicyTopicEntryTypeEnum(
                    entry.type_).name
                policy_topic = entry.topic

            row_dict = {
                'event_date': utils.get_current_date(),
                'customer_id': row.customer.id,
                'customer_descriptive_name': row.customer.descriptive_name,
                'campaign_id': row.campaign.id,
                'campaign_name': row.campaign.name,
                'campaign_status': campaign_status,
                'campaign_primary_status': campaign_primary_status,
                'ad_group_id': row.ad_group.id,
                'ad_group_name': row.ad_group.name,
                'ad_group_status': ad_group_status,
                'ad_id': row.ad_group_ad.ad.id,
                'ad_group_ad_status': ad_group_ad_status,
                'policy_summary_approval_status': policy_approval_status,
                'ad_policy_summary_policy_topic_entry_topic': policy_topic,
                'ad_policy_summary_policy_topic_entry_type': policy_type,
                'ad_policy_summary_review_status': policy_review_status,
            }

            rows_to_insert.append(row_dict)

    return pd.DataFrame(rows_to_insert)


def load_gaql_query(sql_file: str = 'gaql.sql') -> str:
    """Open the SQL file and return the query with the comments stripped."""
    logger.info('Loading Google Ads Query Language query.')
    with open(sql_file, 'r') as f:
        query = f.read()
        query = sqlparse.format(query, strip_comments=True).strip()
        # logger.info(query)
    return query


def get_ads_client(config: models.Config) -> GoogleAdsClient:
    """Get a Google Ads Client based on the config."""
    logger.info('Getting Google Ads client.')
    credentials = {
        'developer_token': config.google_ads_developer_token.get_secret_value(),
        'refresh_token': config.oauth_refresh_token.get_secret_value(),
        'client_id': config.google_cloud_client_id,
        'client_secret': config.google_cloud_client_secret.get_secret_value(),
        'use_proto_plus': True,
        'login_customer_id': config.google_ads_login_customer_id,
    }
    return GoogleAdsClient.load_from_dict(credentials)
