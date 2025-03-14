-- Copyright 2024 Google LLC
--
-- Licensed under the Apache License, Version 2.0 (the "License");
-- you may not use this file except in compliance with the License.
-- You may obtain a copy of the License at
--
--     https://www.apache.org/licenses/LICENSE-2.0
--
-- Unless required by applicable law or agreed to in writing, software
-- distributed under the License is distributed on an "AS IS" BASIS,
-- WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
-- See the License for the specific language governing permissions and
-- limitations under the License.
SELECT 
  "{yesterday}" AS event_date,
  customer.id,
  customer.descriptive_name,
  asset.id,
  asset.source,
  asset.type,
  asset.policy_summary.review_status AS asset_policy_summary_review_status,
  asset.policy_summary.policy_topic_entries:topic AS asset_policy_summary_policy_topic_entries_topics,
  asset.policy_summary.approval_status AS asset_policy_summary_approval_status,
  campaign.id,
  campaign.status,
  campaign.primary_status,
  ad_group.id,
  ad_group.status
FROM
  ad_group_asset
WHERE
  customer.status = 'ENABLED'
  AND asset.policy_summary.approval_status != 'APPROVED'
  AND campaign.status = 'ENABLED'
  AND campaign.primary_status != 'ENDED'
  AND ad_group.status = 'ENABLED'
  AND segments.date DURING LAST_30_DAYS
