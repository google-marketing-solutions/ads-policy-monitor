provider "google" {
  project = var.project_id
  region  = var.region
}

# SERVICE ACCOUNT --------------------------------------------------------------
resource "google_service_account" "service_account" {
  account_id   = "ads-policy-monitor"
  display_name = "Service Account for running Ads Policy Monitor"
}
resource "google_project_iam_member" "cloud_run_invoker_role" {
  project = var.project_id
  role    = "roles/run.invoker"
  member  = "serviceAccount:${google_service_account.service_account.email}"
}
resource "google_project_iam_member" "bigquery_admin_role" {
  project = var.project_id
  role    = "roles/bigquery.admin"
  member  = "serviceAccount:${google_service_account.service_account.email}"
}
resource "google_project_iam_member" "secret_accessor_role" {
  project = var.project_id
  role    = "roles/secretmanager.secretAccessor"
  member  = "serviceAccount:${google_service_account.service_account.email}"
}

# BIGQUERY ---------------------------------------------------------------------
resource "google_bigquery_dataset" "dataset" {
  dataset_id                  = var.bq_output_dataset
  location                    = var.region
  description                 = "Ads Policy Monitor BQ Dataset"
  delete_contents_on_destroy  = true
}

resource "google_bigquery_table" "ad_policy_data_table" {
  dataset_id          = google_bigquery_dataset.dataset.dataset_id
  table_id            = "AdPolicyData"
  deletion_protection = false
  schema              = file("../bigquery/schema/ad_policy_data_schema.json")
  time_partitioning {
    type          = "DAY"
    expiration_ms = 86400000 * var.bq_expiration_days
  }
}

resource "google_bigquery_table" "ocid_table" {
  dataset_id          = google_bigquery_dataset.dataset.dataset_id
  table_id            = "Ocid"
  deletion_protection = false
  schema              = file("../bigquery/schema/ocid_schema.json")
}

resource "google_bigquery_table" "no_approved_ads_ad_group_report" {
  dataset_id          = google_bigquery_dataset.dataset.dataset_id
  table_id            = "NoApprovedAdsAdGroup"
  deletion_protection = false
  depends_on          = [
    google_bigquery_dataset.dataset,
    google_bigquery_table.ad_policy_data_table,
  ]
  view {
    query = templatefile(
    "../bigquery/views/no_approved_ads_ad_group.sql",
    {
      BQ_DATASET = google_bigquery_dataset.dataset.dataset_id
    }
    )
    use_legacy_sql = false
  }
  lifecycle {
    replace_triggered_by = [
      google_bigquery_table.ad_policy_data_table
    ]
  }
}

resource "google_bigquery_table" "latest_ad_policy_data_report" {
  dataset_id          = google_bigquery_dataset.dataset.dataset_id
  table_id            = "LatestAdPolicyData"
  deletion_protection = false
  depends_on          = [
    google_bigquery_dataset.dataset,
    google_bigquery_table.ad_policy_data_table,
    google_bigquery_table.ocid_table,
  ]
  view {
    query = templatefile(
      "../bigquery/views/latest_ad_policy_data.sql",
      {
        BQ_DATASET = google_bigquery_dataset.dataset.dataset_id
      }
    )
    use_legacy_sql = false
  }
  lifecycle {
    replace_triggered_by = [
      google_bigquery_table.ad_policy_data_table
    ]
  }
}

# CLOUD STORAGE ----------------------------------------------------------------
# This bucket is used to store the cloud functions for deployment.
# The project ID is used to make sure the name is globally unique
resource "google_storage_bucket" "function_bucket" {
  name                        = "${var.project_id}-functions"
  location                    = var.region
  force_destroy               = true
  uniform_bucket_level_access = true

  lifecycle_rule {
    condition {
      age = 1
    }
    action {
      type = "Delete"
    }
  }
}

# CLOUD FUNCTIONS --------------------------------------------------------------
data "archive_file" "ads_policy_monitor_zip" {
  type        = "zip"
  output_path = ".temp/ads_policy_monitor_source.zip"
  source_dir  = "../cloud_functions/ads_policy_monitor"
}
resource "google_storage_bucket_object" "google_ad_policy_data" {
  name       = "ads_policy_monitor_${data.archive_file.ads_policy_monitor_zip.output_md5}.zip"
  bucket     = google_storage_bucket.function_bucket.name
  source     = data.archive_file.ads_policy_monitor_zip.output_path
  depends_on = [data.archive_file.ads_policy_monitor_zip]
}

resource "google_cloudfunctions2_function" "fetch_ads_policy_monitor_function" {
  location              = var.region
  name                  = "ads_policy_monitor"
  description           = "Fetches policy approval data from running Google Ads campaigns."

  build_config {
    runtime     = "python311"
    entry_point = "main"
    source {
      storage_source {
        bucket = google_storage_bucket.function_bucket.name
        object = google_storage_bucket_object.google_ad_policy_data.name
      }
    }
  }
  service_config {
    available_memory      = "1G"
    timeout_seconds       = 3600
    service_account_email = google_service_account.service_account.email

    secret_environment_variables {
      project_id = var.project_id
      key        = "GOOGLE_ADS_REFRESH_TOKEN"
      secret     = google_secret_manager_secret.oauth_refresh_token_secret.secret_id
      version    = "latest"
    }
    secret_environment_variables {
      project_id = var.project_id
      key        = "GOOGLE_ADS_CLIENT_ID"
      secret     = google_secret_manager_secret.client_id_secret.secret_id
      version    = "latest"
    }
    secret_environment_variables {
      project_id = var.project_id
      key        = "GOOGLE_ADS_CLIENT_SECRET"
      secret     = google_secret_manager_secret.client_secret_secret.secret_id
      version    = "latest"
    }
    secret_environment_variables {
      project_id = var.project_id
      key        = "GOOGLE_ADS_DEVELOPER_TOKEN"
      secret     = google_secret_manager_secret.developer_token_secret.secret_id
      version    = "latest"
    }
  }
}

# CLOUD_SCHEDULER --------------------------------------------------------------
locals {
  scheduler_body = templatefile("${path.module}/scheduler.tmpl", {
    project_id = var.project_id
    bq_output_dataset = var.bq_output_dataset
    region = var.region
    google_ads_login_customer_id = var.google_ads_login_customer_id
    customer_ids = var.customer_ids
  })
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
    uri         = google_cloudfunctions2_function.fetch_ads_policy_monitor_function.service_config[0].uri
    body        = base64encode(local.scheduler_body)
    headers     = {
      "Content-Type" = "application/json"
    }
    oidc_token {
      service_account_email = google_service_account.service_account.email
    }
  }
}

# SECRET MANAGER ---------------------------------------------------------------
resource "google_secret_manager_secret" "oauth_refresh_token_secret" {
  secret_id = "ads-policy-monitor-oauth-refresh-token-secret"
  replication {
    auto {}
  }
}
resource "google_secret_manager_secret" "client_id_secret" {
  secret_id = "ads-policy-monitor-client-id-secret"
  replication {
    auto {}
  }
}
resource "google_secret_manager_secret" "client_secret_secret" {
  secret_id = "ads-policy-monitor-client-secret-secret"
  replication {
    auto {}
  }
}
resource "google_secret_manager_secret" "developer_token_secret" {
  secret_id = "ads-policy-monitor-developer-token-secret"
  replication {
    auto {}
  }
}

resource "google_secret_manager_secret_version" "oauth_refresh_token_secret_version" {
  secret = google_secret_manager_secret.oauth_refresh_token_secret.id
  secret_data = var.oauth_refresh_token
}
resource "google_secret_manager_secret_version" "client_id_secret_version" {
  secret = google_secret_manager_secret.client_id_secret.id
  secret_data = var.google_cloud_client_id
}
resource "google_secret_manager_secret_version" "client_secret_secret_version" {
  secret = google_secret_manager_secret.client_secret_secret.id
  secret_data = var.google_cloud_client_secret
}
resource "google_secret_manager_secret_version" "developer_token_secret_version" {
  secret = google_secret_manager_secret.developer_token_secret.id
  secret_data = var.google_ads_developer_token
}
