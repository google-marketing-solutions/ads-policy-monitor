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
 * A view that shows ad groups that have no approved ads.
 */
WITH AdCounts AS (
  SELECT
    customer_id,
    customer_descriptive_name,
    ad_group_id,
    ad_group_name,
    CONCAT("https://ads.google.com/aw/overview?ocid=", Ocid.ocid) AS gads_link,
    COUNT(*) AS number_of_ads,
  FROM
    `${BQ_DATASET}.AdPolicyData` AS AdPolicyData
  LEFT JOIN
    `${BQ_DATASET}.Ocid` AS Ocid ON
    Ocid.account_id = AdPolicyData.customer_id
  WHERE
    CAST(_PARTITIONTIME AS DATE) = CURRENT_DATE()
  GROUP BY
    1,2,3,4,5
),
DisapprovedAds AS (
  SELECT
    customer_id,
    ad_group_id,
    COUNT(*) AS disapproved_ads,
  FROM
    `${BQ_DATASET}.AdPolicyData`
  WHERE
    CAST(_PARTITIONTIME AS DATE) = CURRENT_DATE()
    AND ad_group_ad_policy_summary_approval_status != 'APPROVED'
  GROUP BY
    1,2
)

SELECT
  AdCounts.*,
  DisapprovedAds.disapproved_ads
FROM
  DisapprovedAds
LEFT JOIN
  AdCounts USING(customer_id, ad_group_id)
WHERE
  DisapprovedAds.disapproved_ads = AdCounts.number_of_ads
