#The Google Cloud project ID used for this code.
project_id = ""
#The Google Cloud bucket name to store the terraform state.
bucket_name = "ads-pmd-bucket"
# The region where you would like to store data in BigQuery and other resources (Cloud funtion, scheduler, bucket).
# e.g. europe-west2. Please note: Region selected needs to support Cloud Scheduler. 
# Up to date information on region support can be found at https://cloud.google.com/about/locations
region = ""
# These next variables are for pulling data from Google Ads. Read:
# https://developers.google.com/google-ads/api/docs/get-started/introduction
# For more information on how to obtain these tokens.
oauth_refresh_token = ""
google_cloud_client_id = ""
google_cloud_client_secret = ""
google_ads_developer_token = ""
google_ads_login_customer_id = ""
# These are the Google Ads customer IDs you would like to run the tool for.
# It is a list of IDs and should have no dashes. For example:
#[1111111111, 2222222222]
customer_ids = []
# This is where you would like to output the policy data to in BigQuery.
# These resources will be created.
bq_output_dataset = ""
# How long should you store the historical data in BigQuery partitions in days?
bq_expiration_days = 90
# Set this to true if you want to deploy the demo dashboard with synthetic data,
# otherwise set false. If this is false it will pull data from Google Ads.
use_synthetic_data = false
