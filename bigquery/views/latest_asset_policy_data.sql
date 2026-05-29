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
-- Step 0: Normalize the policy strings by sorting the topics alphabetically
WITH NormalizedData AS (
  SELECT
    *,
    -- This subquery splits the topics, sorts them, and rejoins them into a canonical string
    (
      SELECT STRING_AGG(topic, '|' ORDER BY topic)
      FROM UNNEST(SPLIT(IFNULL(asset_policy_summary_policy_topic_entries_topics, ''), '|')) AS topic
    ) AS normalized_policy_topics
  FROM
    `${BQ_DATASET}.AssetPolicyData`
),
-- Step 1: Identify contiguous blocks (islands) of the same asset policy status
StatusWithBlockIDs AS (
  SELECT
    customer_id,
    asset_id,
    asset_policy_summary_approval_status,
    normalized_policy_topics,
    event_date,
    -- This SUM creates a unique ID for each continuous block of the same status.
    -- The counter increases by 1 only when the policy topic string changes from the previous day.
    SUM(is_new_block) OVER (
      PARTITION BY customer_id, asset_id
      ORDER BY event_date
    ) AS block_id
  FROM (
    -- This inner query detects if the policy on a given day is different from the previous day
    SELECT
      customer_id,
      asset_id,
      asset_policy_summary_approval_status,
      normalized_policy_topics,
      DATE(event_date) as event_date,
      CASE
        WHEN
          CONCAT(asset_policy_summary_approval_status, normalized_policy_topics)
          !=
          LAG(CONCAT(asset_policy_summary_approval_status, normalized_policy_topics), 1, '') OVER (
            PARTITION BY customer_id, asset_id
            ORDER BY DATE(event_date)
          )
        THEN 1
        ELSE 0
      END AS is_new_block
    FROM
      NormalizedData
  )
),
-- Step 2: For each block, find its start date
BlockStartDates AS (
  SELECT
    customer_id,
    asset_id,
    block_id,
    MIN(event_date) AS policy_status_updated_date
  FROM StatusWithBlockIDs
  GROUP BY 1, 2, 3
)
-- Step 3: Join everything back to today's data
SELECT
  Ocid.ocid,
  STRUCT(
    CONCAT('https://ads.google.com/aw/overview?ocid=', Ocid.ocid) AS home,
    CONCAT('https://ads.google.com/aw/assetreport/associations/allupgraded',
    '?ocid=', Ocid.ocid,
    IF(AssetPolicyData.example_campaign_id is Null, '', '&campaignId=' || AssetPolicyData.example_campaign_id),
    IF(AssetPolicyData.example_ad_group_id is Null, '', '&adGroupId=' || AssetPolicyData.example_ad_group_id)
    ) AS assets
  ) AS gads_links,
  AssetPolicyData.*,
  -- This is the new column with the start date of the current policy
  BlockDates.policy_status_updated_date,
  SPLIT(
    REPLACE(AssetPolicyData.normalized_policy_topics, ' ', ''),
    '|') AS asset_policy_topics
FROM
  NormalizedData AS AssetPolicyData
LEFT JOIN
  (
    SELECT DISTINCT account_id, ocid FROM `${BQ_DATASET}.Ocid`
  ) AS Ocid ON Ocid.account_id = AssetPolicyData.customer_id
-- Join to get the block_id for TODAY's status
LEFT JOIN StatusWithBlockIDs AS CurrentBlock
  ON AssetPolicyData.customer_id = CurrentBlock.customer_id
  AND AssetPolicyData.asset_id = CurrentBlock.asset_id
  AND DATE(AssetPolicyData.event_date) = CurrentBlock.event_date
-- Join to get the start date for that specific block_id
LEFT JOIN BlockStartDates AS BlockDates
  ON CurrentBlock.customer_id = BlockDates.customer_id
  AND CurrentBlock.asset_id = BlockDates.asset_id
  AND CurrentBlock.block_id = BlockDates.block_id
WHERE Date(AssetPolicyData.event_date) = CURRENT_DATE()