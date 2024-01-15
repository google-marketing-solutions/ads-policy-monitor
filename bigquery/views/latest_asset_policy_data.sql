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
SELECT
  Ocid.ocid,
  STRUCT(
    CONCAT("https://ads.google.com/aw/overview?ocid=", Ocid.ocid) AS home,
    CONCAT("https://ads.google.com/aw/assetreport/associations/", REPLACE(LOWER(AssetPolicyData.asset_type),'_',''),
    "?ocid=", Ocid.ocid
    ) AS assets
   ) AS gads_links,
  AssetPolicyData.*,
  SPLIT(
    AssetPolicyData.asset_policy_summary_policy_topic_entries_topics,
    "|") AS asset_policy_topics,
FROM
  `${BQ_DATASET}.AssetPolicyData` AS AssetPolicyData
LEFT JOIN
  (
    SELECT DISTINCT account_id, ocid FROM `${BQ_DATASET}.Ocid`
  ) AS Ocid ON Ocid.account_id = AssetPolicyData.customer_id
WHERE
  EXTRACT(DATE FROM _PARTITIONTIME) = CURRENT_DATE()
