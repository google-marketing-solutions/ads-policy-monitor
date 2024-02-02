#!/bin/bash
#
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


# Get bucket name and region from terraform env variables file.
TFVARS_FILE="./terraform/example.tfvars"
REGION=$(grep 'region' $TFVARS_FILE | awk -F= '{print $2}' | tr -d '"' | xargs)
BUCKET_NAME=$(grep 'bucket_name' $TFVARS_FILE | awk -F= '{print $2}' | tr -d '"' | xargs)
DATASET_ID=$(grep 'bq_output_dataset' $TFVARS_FILE | awk -F= '{print $2}' | tr -d '"' | xargs)
PROJECT_ID=$(grep 'project_id' $TFVARS_FILE | awk -F= '{print $2}' | tr -d '"' | xargs)
TEMPLATE_LINK="https://lookerstudio.google.com/reporting/create?\
c.mode=edit&c.reportId=13995d1f-741c-40f0-934c-9517e2ffc361&\
r.reportName=Ads%20Policy%20Monitor&ds.*.refreshFields=false&\
ds.LatestAdPolicyData.connector=bigQuery&\
ds.LatestAdPolicyData.datasourceName=LatestAdPolicyData&\
ds.LatestAdPolicyData.projectId=$PROJECT_ID&\
ds.LatestAdPolicyData.datasetId=$DATASET_ID&\
ds.LatestAdPolicyData.type=TABLE&\
ds.LatestAdPolicyData.tableId=LatestAdPolicyData&\
ds.AdPolicyDataTimeSeries.connector=bigQuery&\
ds.AdPolicyDataTimeSeries.datasourceName=AdPolicyDataTimeSeries&\
ds.AdPolicyDataTimeSeries.projectId=$PROJECT_ID&\
ds.AdPolicyDataTimeSeries.datasetId=$DATASET_ID&\
ds.AdPolicyDataTimeSeries.type=TABLE&\
ds.AdPolicyDataTimeSeries.tableId=AdPolicyDataTimeSeries&\
ds.LatestAssetPolicyData.connector=bigQuery&\
ds.LatestAssetPolicyData.datasourceName=LatestAssetPolicyData&\
ds.LatestAssetPolicyData.projectId=$PROJECT_ID&\
ds.LatestAssetPolicyData.datasetId=$DATASET_ID&\
ds.LatestAssetPolicyData.type=TABLE&\
ds.LatestAssetPolicyData.tableId=LatestAssetPolicyData&\
ds.AssetPolicyDataTimeSeries.connector=bigQuery&\
ds.AssetPolicyDataTimeSeries.datasourceName=AssetPolicyDataTimeSeries&\
ds.AssetPolicyDataTimeSeries.projectId=$PROJECT_ID&\
ds.AssetPolicyDataTimeSeries.datasetId=$DATASET_ID&\
ds.AssetPolicyDataTimeSeries.type=TABLE&\
ds.AssetPolicyDataTimeSeries.tableId=AssetPolicyDataTimeSeries&\
ds.NoApprovedAdsAdGroup.connector=bigQuery&\
ds.NoApprovedAdsAdGroup.datasourceName=NoApprovedAdsAdGroup&\
ds.NoApprovedAdsAdGroup.projectId=$PROJECT_ID&\
ds.NoApprovedAdsAdGroup.datasetId=$DATASET_ID&\
ds.NoApprovedAdsAdGroup.type=TABLE&\
ds.NoApprovedAdsAdGroup.tableId=NoApprovedAdsAdGroup"

# Get current cloud project ID
pr=$DEVSHELL_PROJECT_ID

echo "Google Cloud Project selection confirmation..."
until [[ "$yn" == [YyNn] ]]; do
    proceed_with_project="You are about to install the Ads Policy Monitor into "
    proceed_with_project+="the following project: $DEVSHELL_PROJECT_ID. Proceed? (y/n): "
    read -p "$proceed_with_project" yn
done

if [[ "$yn" == "n"  || "$yn" == "N" ]]; then
    echo "Please fix project_id variable with the correct project in the tfvars file (terraform/example.tfvars)"
    exit 1
fi

echo "Creating a Cloud Storage Bucket $BUCKET_NAME in region $REGION..."
gcloud storage buckets create "gs://$BUCKET_NAME" --location=$REGION

if [ $? -eq 0 ]; then
  echo "Enabling required APIs..."
  gcloud services enable \
    bigquery.googleapis.com \
    cloudbuild.googleapis.com \
    cloudfunctions.googleapis.com \
    cloudresourcemanager.googleapis.com \
    googleads.googleapis.com \
    iam.googleapis.com \
    secretmanager.googleapis.com \
    run.googleapis.com \
    cloudscheduler.googleapis.com

  echo "Initializing terraform..."
  cd terraform
  terraform init -backend-config="bucket=$BUCKET_NAME"
  terraform apply --var-file example.tfvars && {
      echo -e "\e[32mTerraform apply was successful.\e[0m"

      echo "If you wish to use the Looker templated provided, click the link below to set up your dashboard:"
      echo -e "\e[36m$TEMPLATE_LINK\e[0m"
      echo -e "\nPlease note: You need to be part of the readers group as detailed on deployment requirements: https://groups.google.com/g/ads-policy-monitor-template-readers"
  } || {
      echo "Terraform apply failed."
  }
else
  exit 1
fi