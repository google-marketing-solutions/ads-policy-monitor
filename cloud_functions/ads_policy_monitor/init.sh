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
  terraform apply --var-file example.tfvars
else
  exit 1
fi