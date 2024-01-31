# Copyright 2024 Google LLC
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
"""Constants file for unit tests"""

TEST_AD_GROUP_ASSET_POLICY_DATA = {
    'event_date': ['2023-10-26', '2023-10-26', '2023-10-26'],
    'customer_id': [12345, 12345, 12345],
    'customer_descriptive_name': ['Customer A', 'Customer A', 'Customer A'],
    'asset_id': [11, 21, 21],
    'asset_source': ['ADVERTISER', 'ADVERTISER', 'ADVERTISER'],
    'asset_type': ['CALLOUT', 'CALLOUT', 'CALLOUT'],
    'asset_policy_summary_review_status': ['REVIEWED', 'REVIEWED', 'REVIEWED'],
    'asset_policy_summary_policy_topic_entries_topics': [
        ['TRADEMARKS_IN_AD_TEXT', 'TOBACO'],
        'TRADEMARKS_IN_AD_TEXT',
        'TRADEMARKS_IN_AD_TEXT',
    ],
    'asset_policy_summary_approval_status': [
        'APPROVED_LIMITED',
        'APPROVED_LIMITED',
        'APPROVED_LIMITED',
    ],
    'campaign_id': [1, 1, 1],
    'campaign_status': ['ENABLED', 'ENABLED', 'ENABLED'],
    'ad_group_id': [1, 2, 3],
    'ad_group_status': ['ENABLED', 'ENABLED', 'ENABLED'],
}

TEST_CAMPAIGN_ASSET_POLICY_DATA = {
    'event_date': ['2023-10-26', '2023-10-26', '2023-10-26', '2023-10-27'],
    'customer_id': [12345, 12345, 12345, 12345],
    'customer_descriptive_name': [
        'Customer A', 'Customer A', 'Customer A', 'Customer A'
    ],
    'asset_id': [22, 22, 22, 22],
    'asset_source': ['ADVERTISER', 'ADVERTISER', 'ADVERTISER', 'ADVERTISER'],
    'asset_type': ['CALLOUT', 'CALLOUT', 'CALLOUT', 'CALLOUT'],
    'asset_policy_summary_review_status': [
        'REVIEWED', 'REVIEWED', 'REVIEWED', 'REVIEWED'
    ],
    'asset_policy_summary_policy_topic_entries_topics': [
        'TRADEMARKS_IN_AD_TEXT',
        'TRADEMARKS_IN_AD_TEXT',
        'TRADEMARKS_IN_AD_TEXT',
        'TRADEMARKS_IN_AD_TEXT',
    ],
    'asset_policy_summary_approval_status': [
        'APPROVED_LIMITED',
        'APPROVED_LIMITED',
        'APPROVED_LIMITED',
        'APPROVED_LIMITED',
    ],
    'campaign_id': [1, 2, 3, 3],
    'campaign_status': ['ENABLED', 'ENABLED', 'ENABLED', 'ENABLED'],
}

TEST_CUSTOMER_ASSET_POLICY_DATA = {
    'event_date': ['2023-10-26', '2023-10-26', '2023-10-26'],
    'customer_id': [12345, 12345, 12345],
    'customer_descriptive_name': ['Customer A', 'Customer A', 'Customer A'],
    'asset_id': [13, 23, 33],
    'asset_source': ['ADVERTISER', 'ADVERTISER', 'ADVERTISER'],
    'asset_type': ['CALLOUT', 'CALLOUT', 'CALLOUT'],
    'asset_policy_summary_review_status': ['REVIEWED', 'REVIEWED', 'REVIEWED'],
    'asset_policy_summary_policy_topic_entries_topics': [
        'TRADEMARKS_IN_AD_TEXT',
        'TRADEMARKS_IN_AD_TEXT',
        'TRADEMARKS_IN_AD_TEXT',
    ],
    'asset_policy_summary_approval_status': [
        'APPROVED_LIMITED',
        'APPROVED_LIMITED',
        'APPROVED_LIMITED',
    ],
}

TEST_EXPECTED_ASSET_POLICY_REPORT = {
    'event_date': [
        '2023-10-26',
        '2023-10-26',
        '2023-10-26',
        '2023-10-27',
        '2023-10-26',
        '2023-10-26',
        '2023-10-26',
    ],
    'customer_id': [12345, 12345, 12345, 12345, 12345, 12345, 12345],
    'customer_descriptive_name': [
        'Customer A',
        'Customer A',
        'Customer A',
        'Customer A',
        'Customer A',
        'Customer A',
        'Customer A',
    ],
    'asset_id': [11, 21, 22, 22, 13, 23, 33],
    'asset_source': [
        'ADVERTISER',
        'ADVERTISER',
        'ADVERTISER',
        'ADVERTISER',
        'ADVERTISER',
        'ADVERTISER',
        'ADVERTISER',
    ],
    'asset_type': [
        'CALLOUT',
        'CALLOUT',
        'CALLOUT',
        'CALLOUT',
        'CALLOUT',
        'CALLOUT',
        'CALLOUT',
    ],
    'asset_policy_summary_review_status': [
        'REVIEWED',
        'REVIEWED',
        'REVIEWED',
        'REVIEWED',
        'REVIEWED',
        'REVIEWED',
        'REVIEWED',
    ],
    'asset_policy_summary_policy_topic_entries_topics': [
        'TRADEMARKS_IN_AD_TEXT | TOBACO',
        'TRADEMARKS_IN_AD_TEXT',
        'TRADEMARKS_IN_AD_TEXT',
        'TRADEMARKS_IN_AD_TEXT',
        'TRADEMARKS_IN_AD_TEXT',
        'TRADEMARKS_IN_AD_TEXT',
        'TRADEMARKS_IN_AD_TEXT',
    ],
    'asset_policy_summary_approval_status': [
        'APPROVED_LIMITED',
        'APPROVED_LIMITED',
        'APPROVED_LIMITED',
        'APPROVED_LIMITED',
        'APPROVED_LIMITED',
        'APPROVED_LIMITED',
        'APPROVED_LIMITED',
    ],
    'asset_level': [
        'Ad Group',
        'Ad Group',
        'Campaign',
        'Campaign',
        'Account',
        'Account',
        'Account',
    ],
    'counts': [1, 2, 3, 1, 1, 1, 1],
}

TEST_CUSTOMER_ASSET_POLICY_DATA_EMPTY = {
    'event_date': ['2023-10-26'],
    'customer_id': [0],
    'customer_descriptive_name': [''],
    'asset_id': [0],
    'asset_source': ['UNSPECIFIED'],
    'asset_type': ['UNSPECIFIED'],
    'asset_policy_summary_review_status': ['UNSPECIFIED'],
    'asset_policy_summary_policy_topic_entries_topics': [''],
    'asset_policy_summary_approval_status': ['UNSPECIFIED']
}

TEST_EXPECTED_ASSET_POLICY_REPORT_EMPTY_CUSTOMER = {
    'event_date': ['2023-10-26', '2023-10-26', '2023-10-26', '2023-10-27'],
    'customer_id': [12345, 12345, 12345, 12345],
    'customer_descriptive_name': [
        'Customer A', 'Customer A', 'Customer A', 'Customer A'
    ],
    'asset_id': [11, 21, 22, 22],
    'asset_source': ['ADVERTISER', 'ADVERTISER', 'ADVERTISER', 'ADVERTISER'],
    'asset_type': ['CALLOUT', 'CALLOUT', 'CALLOUT', 'CALLOUT'],
    'asset_policy_summary_review_status': [
        'REVIEWED', 'REVIEWED', 'REVIEWED', 'REVIEWED'
    ],
    'asset_policy_summary_policy_topic_entries_topics': [
        'TRADEMARKS_IN_AD_TEXT | TOBACO', 'TRADEMARKS_IN_AD_TEXT',
        'TRADEMARKS_IN_AD_TEXT', 'TRADEMARKS_IN_AD_TEXT'
    ],
    'asset_policy_summary_approval_status': [
        'APPROVED_LIMITED', 'APPROVED_LIMITED', 'APPROVED_LIMITED',
        'APPROVED_LIMITED'
    ],
    'asset_level': ['Ad Group', 'Ad Group', 'Campaign', 'Campaign'],
    'counts': [1, 2, 3, 1],
}

TEST_EXPECTED_TIME_SERIES = {
    'event_date': ['2023-10-26', '2023-10-27'],
    'asset_policy_summary_approval_status': [
        'APPROVED_LIMITED', 'APPROVED_LIMITED'
    ],
    'counts': [3, 1]
}
