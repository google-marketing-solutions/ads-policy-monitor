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
 * A view that combines ocid with the latest data ads policy data.
 */
SELECT
  Ocid.ocid,
  CONCAT("https://ads.google.com/aw/overview?ocid=", Ocid.ocid) AS gads_link,
  AdPolicyData.*,
  SPLIT(
    AdPolicyData.ad_group_ad_policy_summary_policy_topic_entries,
    "|") AS ad_policy_topics,
FROM
  `${BQ_DATASET}.AdPolicyData` AS AdPolicyData
LEFT JOIN
  `${BQ_DATASET}.Ocid` AS Ocid ON
  Ocid.account_id = AdPolicyData.customer_id
WHERE
  EXTRACT(DATE FROM _PARTITIONTIME) = CURRENT_DATE()
