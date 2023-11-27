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

bucketname='ads_policy_monitor'
pr=$DEVSHELL_PROJECT_ID

echo "Google Cloud Project selection..."
until [[ "$yn" == [YyNn] ]]; do
    proceed_with_project="You are about to install the Ads Policy Monitor into "
    proceed_with_project+="the following project: $DEVSHELL_PROJECT_ID. Proceed? (y/n): "
    read -p "$proceed_with_project" yn
done

if [[ "$yn" == "n"  || "$yn" == "N" ]]; then
    read -p "In which project should the solution be installed on?:" pr
    gcloud config set project "$pr"
fi

echo "Setting project_id in tfvars file..."
echo 'project_id = "'"$pr"'"'  >> ./terraform/example.tfvars

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

echo "Creating a Cloud Storage Bucket..."
gcloud storage buckets create "gs://$bucketname"

pwd 

echo "Initializing terraform..."
cd terraform
terraform init -backend-config="bucket=$bucketname"
terraform apply --var-file example.tfvars
