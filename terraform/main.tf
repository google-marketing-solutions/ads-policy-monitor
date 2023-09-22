provider "google" {
  project = var.project_id
  region  = var.region
}

# SERVICE ACCOUNT --------------------------------------------------------------
resource "google_service_account" "service_account" {
  account_id   = "ads-policy-monitor"
  display_name = "Service Account for running Ads Policy Monitor"
}
resource "google_project_iam_member" "cloud_functions_invoker_role" {
  project = var.project_id
  role    = "roles/cloudfunctions.invoker"
  member  = "serviceAccount:${google_service_account.service_account.email}"
}
resource "google_project_iam_member" "bigquery_job_user_role" {
  project = var.project_id
  role    = "roles/bigquery.jobUser"
  member  = "serviceAccount:${google_service_account.service_account.email}"
}
resource "google_project_iam_member" "bigquery_data_viewer_role" {
  project = var.project_id
  role    = "roles/bigquery.dataViewer"
  member  = "serviceAccount:${google_service_account.service_account.email}"
}


# BIGQUERY ---------------------------------------------------------------------
resource "google_bigquery_dataset" "dataset" {
  dataset_id                  = var.bq_output_dataset
  location                    = var.region
  description                 = "Ads Policy Monitor BQ Dataset"
  delete_contents_on_destroy  = true
}

resource "google_bigquery_table" "google_ads_policy_table" {
  dataset_id          = google_bigquery_dataset.dataset.dataset_id
  table_id            = var.bq_output_table
  deletion_protection = false
}

# CLOUD FUNCTIONS --------------------------------------------------------------
resource "google_cloudfunctions_function" "fetch_ads_policy_data_function" {
  region                = var.region
  name                  = "fetch_ads_policy"
  description           = "Fetches policy approval data from running Google Ads campaigns."
  runtime               = "python311"
  service_account_email = google_service_account.service_account.email
  timeout               = 540
  available_memory_mb   = 1024
  entry_point           = "main"
  trigger_http          = true
}

# CLOUD_SCHEDULER --------------------------------------------------------------
locals {
  scheduler_body = <<EOF
    {
        "project_id": "${var.project_id}"
        "bq_output_dataset": "${var.bq_output_dataset}"
        "bq_output_table": "${var.bq_output_table}"
        "google_ads_developer_token": "${var.google_ads_developer_token}"
        "oauth_refresh_token": "${var.oauth_refresh_token}"
        "google_cloud_client_id": "${var.google_cloud_client_id}"
        "google_cloud_client_secret": "${var.google_cloud_client_secret}"
        "google_ads_login_customer_id": "${var.google_ads_login_customer_id}"
        "customer_ids": "${var.customer_ids}"
    }
    EOF
}
resource "google_cloud_scheduler_job" "ads_policy_daily_scheduler" {
  name             = "ads_policy_monitor"
  description      = "Run the Ads Policy Monitor pipeline"
  schedule         = "0 0 * * *"
  time_zone        = "Etc/UTC"
  attempt_deadline = "320s"
  region           = var.region

  http_target {
    http_method = "POST"
    uri         = google_cloudfunctions_function.fetch_ads_policy_data_function.https_trigger_url
    body        = base64encode(local.scheduler_body)
    headers     = {
      "Content-Type" = "application/json"
    }
    oidc_token {
      service_account_email = google_service_account.service_account.email
    }
  }
}