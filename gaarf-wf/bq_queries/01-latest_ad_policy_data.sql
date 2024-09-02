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
/**
 * Pull the latest Ad Policy Data combined with deep links to Google Ads.
 */
 
CREATE SCHEMA IF NOT EXISTS `{bq_dataset}_bq`;
CREATE OR REPLACE TABLE `{bq_dataset}_bq.latest_ad_policy_data` AS
SELECT
  Ocid.ocid,
  STRUCT(
    CONCAT("https://ads.google.com/aw/overview?ocid=", Ocid.ocid) AS home,
    CONCAT(
    "https://ads.google.com/aw/ads?campaignId=", AdPolicyData.campaign_id,
    "&adGroupId=", AdPolicyData.ad_group_id,
    "&ocid=", Ocid.ocid) AS ads
   ) AS gads_links,
  AdPolicyData.*,
  SPLIT(ARRAY_TO_STRING(AdPolicyData.ad_group_ad_policy_summary_policy_topic_entries, "|"),"|") AS ad_policy_topics,
FROM
  `{bq_dataset}.ad_policy_data` AS AdPolicyData
LEFT JOIN
  (
    SELECT DISTINCT customer_id, ocid FROM `{bq_dataset}.ocid_mapping`
  ) AS Ocid ON Ocid.customer_id = AdPolicyData.customer_id
WHERE Date(event_date) = CURRENT_DATE()-1