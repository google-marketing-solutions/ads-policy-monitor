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
/**
 * Pull the latest Asset Policy Data combined with deep links to Google Ads.
 */
 
CREATE SCHEMA IF NOT EXISTS `{bq_dataset}_bq`;
CREATE OR REPLACE TABLE `{bq_dataset}_bq.latest_asset_policy_data` AS
SELECT
  CURRENT_DATE()-1 AS event_date,
  Ocid.ocid,
  STRUCT(
    CONCAT("https://ads.google.com/aw/overview?ocid=", Ocid.ocid) AS home,
    CONCAT("https://ads.google.com/aw/assetreport/associations/allupgraded",
    "?ocid=", Ocid.ocid,
    IF(AssetPolicyData.campaign_id is Null, "", "&campaignId=" || AssetPolicyData.campaign_id),
    IF(AssetPolicyData.ad_group_id is Null, "", "&adGroupId=" || AssetPolicyData.ad_group_id)
    ) AS assets
   ) AS gads_links,
  AssetPolicyData.customer_id,
  AssetPolicyData.customer_descriptive_name,
  AssetPolicyData.asset_id,
  AssetPolicyData.asset_type,
  AssetPolicyData.asset_source,
  "Ad Group" AS asset_level,
  AssetPolicyData.asset_policy_summary_approval_status AS asset_policy_summary_approval_status,
  AssetPolicyData.asset_policy_summary_review_status AS asset_policy_summary_review_status,
  SPLIT(ARRAY_TO_STRING(AssetPolicyData.asset_policy_summary_policy_topic_entries_topics, "|"),"|") AS asset_policy_summary_policy_topic_entries_topics
FROM
  `{bq_dataset}.ad_group_asset` AS AssetPolicyData
LEFT JOIN
  (
    SELECT DISTINCT customer_id, ocid FROM `{bq_dataset}.ocid_mapping`
  ) AS Ocid ON Ocid.customer_id = AssetPolicyData.customer_id
WHERE Date(event_date) = CURRENT_DATE()-1
UNION ALL
SELECT
  CURRENT_DATE()-1 AS event_date,
  Ocid.ocid,
  STRUCT(
    CONCAT("https://ads.google.com/aw/overview?ocid=", Ocid.ocid) AS home,
    CONCAT("https://ads.google.com/aw/assetreport/associations/allupgraded",
    "?ocid=", Ocid.ocid,
    IF(CampaignAssetPolicyData.campaign_id is Null, "", "&campaignId=" || CampaignAssetPolicyData.campaign_id)
    ) AS assets
   ) AS gads_links,
  CampaignAssetPolicyData.customer_id,
  CampaignAssetPolicyData.customer_descriptive_name,
  CampaignAssetPolicyData.asset_id,
  CampaignAssetPolicyData.asset_type,
  CampaignAssetPolicyData.asset_source,
  "Campaign" AS asset_level,
  CampaignAssetPolicyData.asset_policy_summary_approval_status AS asset_policy_summary_approval_status,
  CampaignAssetPolicyData.asset_policy_summary_review_status AS asset_policy_summary_review_status,
  SPLIT(ARRAY_TO_STRING(CampaignAssetPolicyData.asset_policy_summary_policy_topic_entries_topics, "|"),"|") AS asset_policy_summary_policy_topic_entries_topics
FROM
  `{bq_dataset}.campaign_asset` AS CampaignAssetPolicyData
LEFT JOIN
  (
    SELECT DISTINCT customer_id, ocid FROM `{bq_dataset}.ocid_mapping`
  ) AS Ocid ON Ocid.customer_id = CampaignAssetPolicyData.customer_id
WHERE Date(event_date) = CURRENT_DATE()-1
UNION ALL
SELECT
  CURRENT_DATE()-1 AS event_date,
  Ocid.ocid,
  STRUCT(
    CONCAT("https://ads.google.com/aw/overview?ocid=", Ocid.ocid) AS home,
    CONCAT("https://ads.google.com/aw/assetreport/associations/allupgraded",
    "?ocid=", Ocid.ocid
    ) AS assets
   ) AS gads_links,
  CustomerAssetPolicyData.customer_id,
  CustomerAssetPolicyData.customer_descriptive_name,
  CustomerAssetPolicyData.asset_id,
  CustomerAssetPolicyData.asset_type,
  CustomerAssetPolicyData.asset_source,
  "Account" AS asset_level,
  CustomerAssetPolicyData.asset_policy_summary_approval_status AS asset_policy_summary_approval_status,
  CustomerAssetPolicyData.asset_policy_summary_review_status AS asset_policy_summary_review_status,
  SPLIT(ARRAY_TO_STRING(CustomerAssetPolicyData.asset_policy_summary_policy_topic_entries_topics, "|"),"|") AS asset_policy_summary_policy_topic_entries_topics
FROM
  `{bq_dataset}.customer_asset` AS CustomerAssetPolicyData
LEFT JOIN
  (
    SELECT DISTINCT customer_id, ocid FROM `{bq_dataset}.ocid_mapping`
  ) AS Ocid ON Ocid.customer_id = CustomerAssetPolicyData.customer_id
WHERE Date(event_date) = CURRENT_DATE()-1
UNION ALL
SELECT
  CURRENT_DATE()-1 AS event_date,
  Ocid.ocid,
  STRUCT(
    CONCAT("https://ads.google.com/aw/overview?ocid=", Ocid.ocid) AS home,
    CONCAT("https://ads.google.com/aw/assetreport/associations/allupgraded",
    "?ocid=", Ocid.ocid,
    IF(AssetGroupAssetPolicyData.asset_group_id is Null, "", "&asset_group_id=" || AssetGroupAssetPolicyData.asset_group_id)
    ) AS assets
   ) AS gads_links,
  AssetGroupAssetPolicyData.customer_id,
  AssetGroupAssetPolicyData.customer_descriptive_name,
  AssetGroupAssetPolicyData.asset_id,
  AssetGroupAssetPolicyData.asset_type,
  AssetGroupAssetPolicyData.source AS asset_source,
  "Asset Group" AS asset_level,
  AssetGroupAssetPolicyData.asset_policy_summary_approval_status AS asset_policy_summary_approval_status,
  AssetGroupAssetPolicyData.asset_policy_summary_review_status AS asset_policy_summary_review_status,
  SPLIT(ARRAY_TO_STRING(AssetGroupAssetPolicyData.asset_policy_summary_policy_topic_entries_topics, "|"),"|") AS asset_policy_summary_policy_topic_entries_topics
FROM
  `{bq_dataset}.asset_group_asset` AS AssetGroupAssetPolicyData
LEFT JOIN
  (
    SELECT DISTINCT customer_id, ocid FROM `{bq_dataset}.ocid_mapping`
  ) AS Ocid ON Ocid.customer_id = AssetGroupAssetPolicyData.customer_id