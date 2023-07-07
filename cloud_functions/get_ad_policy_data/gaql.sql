-- Copyright 2023 Google LLC
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
  customer.id,
  customer.descriptive_name,
  campaign.id,
  campaign.name,
  campaign.status,
  campaign.primary_status,
  ad_group.id,
  ad_group.name,
  ad_group.status,
  ad_group_ad.ad.id,
  ad_group_ad.status,
  ad_group_ad.policy_summary.approval_status,
  ad_group_ad.policy_summary.policy_topic_entries,
  ad_group_ad.policy_summary.review_status
FROM
  ad_group_ad
WHERE
  customer.status = 'ENABLED'
