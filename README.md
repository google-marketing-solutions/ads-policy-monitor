# Ads Policy Monitor

_Providing a 1-stop-shop, centralized view of all your Google Ads policy
reports._

Ads Policy Monitor provides a data pipeline for pulling ad and asset approval
data from Google Ads, enabling you to monitor trends and spikes with policy
approvals.

## Solution Overview

To keep ads safe and appropriate for everyone, ads are reviewed to make sure
they comply with Google Ads policies,
[read more here](https://support.google.com/google-ads/answer/1722120?sjid=13030684844768437853-EU).

For large advertisers and agencies, it can be challenging to monitor the state
of your ad copy across all of your Google Ads accounts. This can be amplified
when automation is used to create ad copy, as it's easy to introduce mistakes
that result in ads being disapproved, for example, the incorrect use of
capitalisation.

This solution pulls a daily snapshot of your ad and asset policy approvals,
stores them in BigQuery, and provides a Looker Studio dashboard template to
monitor this.

When disapprovals happen you can take action by following the deeplink into
Google Ads to get more information and take action.

In the dashboard you can instantly monitor the overall status of your accounts:
![Dashboard overview](./docs/images/looker-studio-overview.png)

And how this changes over time. This allows you to identify any changes in the
trend, to investigate further.
![Dashboard time series](./docs/images/looker-studio-time-series.png)

You can drilldown into the disapprovals to try to get more information about why
this has happened:
![Dashboard disapprovals](./docs/images/looker-studio-disapprovals.png)

You're also able to see insights like when an ad group has no approved ads:
![Dashboard no approved ads](./docs/images/looker-studio-no-approved-ads.png)

And analyze asset disapprovals:
![Dashboard assets](./docs/images/looker-studio-assets.png)

## How does it work?

![Architecture diagram](./docs/images/architecture-diagram.png)

1.  A daily cron job runs that makes a HTTPS request to trigger the
    `ads_policy_monitor` Cloud Function.
2.  The Cloud Function uses
    [Google Ads Query Language (GAQL)](https://developers.google.com/google-ads/api/docs/query/overview)
    to run a number of reports in Google Ads via the API.
3.  The output of these reports is written to a dataset in BigQuery called
    `ads_policy_monitor`.
4.  We provide a template Looker Studio dashboard to visualise this data.
    However, there is nothing to stop you using your own dashboard solution. For
    example, it is possible to connect this data with the Looker Platform for
    more advanced BI reporting, alerting, data drilldown etc.

## Requirements

-   A Google Cloud Project
-   Access to the Google Ads API (e.g. developer token, account access),
    [see getting started](https://developers.google.com/google-ads/api/docs/get-started/introduction).
-   Access to Looker Studio or a dashboard solution that can connect to
    BigQuery.
    -   If you wish to have access to the
        [Looker Studio template provided by Google](https://lookerstudio.google.com/c/u/0/reporting/13995d1f-741c-40f0-934c-9517e2ffc361/),
        please join this group
        [ads-policy-monitor-template-readers](https://groups.google.com/g/ads-policy-monitor-template-readers).

## IAM Requirements

To deploy this solution, the user or service account performing the deployment requires specific permissions in the Google Cloud Project.

### Recommended
* **Owner**: To prevent permission errors during deployment, it is explicitly recommended to have the **Project Owner** role (`roles/owner`). This ensures that all APIs can be enabled, resources created, and IAM bindings applied without issues.

### Granular Roles (Optional)
If you prefer to use granular roles instead of Owner, you will need at least the following roles:
* **Service Usage Admin** (`roles/serviceusage.serviceUsageAdmin`): Required by `init.sh` to enable Google Cloud APIs.
* **Storage Admin** (`roles/storage.admin`): Required to create the Terraform state bucket and the function source bucket.
* **Service Account Admin** (`roles/iam.serviceAccountAdmin`): Required to create the solution's service account.
* **Project IAM Admin** (`roles/resourcemanager.projectIamAdmin`): Required to assign roles to the service account.
* **BigQuery Admin** (`roles/bigquery.admin`): Required to create datasets and tables.
* **Cloud Functions Admin** (`roles/cloudfunctions.admin`): Required to deploy the Cloud Function.
* **Cloud Run Admin** (`roles/run.admin`): Required as Cloud Functions (2nd gen) are backed by Cloud Run.
* **Cloud Scheduler Admin** (`roles/cloudscheduler.admin`): Required to create the daily cron job.
* **Secret Manager Admin** (`roles/secretmanager.admin`): Required to store the Google Ads API credentials securely.

## Deployment

1.  Open the Google Cloud Project in the UI.
2.  Open the
    [OAuth Consent Screen](https://console.cloud.google.com/apis/credentials/consent)
    and create a new internal app.
3.  Open the
    <a href="https://pantheon.corp.google.com/apis/credentials" target="_blank">API Credentials Screen</a>
    -> Create credentials -> OAuth Client ID -> Web app -> Set
    `https://developers.google.com/oauthplayground` as an authorised redirect
    URI. Make a note of the `client_id` and the `client_secret`.
4.  Open the
    <a href="https://developers.google.com/oauthplayground/#step1&scopes=https%3A//www.googleapis.com/auth/adwords&url=https%3A//&content_type=application/json&http_method=GET&useDefaultOauthCred=checked&oauthEndpointSelect=Google&oauthAuthEndpointValue=https%3A//accounts.google.com/o/oauth2/v2/auth&oauthTokenEndpointValue=https%3A//oauth2.googleapis.com/token&includeCredentials=unchecked&accessTokenType=bearer&autoRefreshToken=unchecked&accessType=offline&forceAprovalPrompt=checked&response_type=code" target="_blank">OAuth Playground</a>
    to generate a refresh token for the Adwords scope, using the `client_id` and
    `client_secret` generated in the previous step. Please refer to <a href="https://youtu.be/KFICa7Ngzng?si=06HnIrM9il5KAX62&t=439" target="_blank">this video</a> for a demo of how to generate the refresh token.
5.  Open Cloud Shell
6.  Clone the repo & open the directory with the code: 
    ```
    git clone https://github.com/google-marketing-solutions/ads-policy-monitor.git
    ```
7.  Go to `Terminal` -> `New Terminal` from the menu. Make sure you're in the
    intended Cloud project. Otherwise, set the shell to use the correct cloud
    project: 
    ```
    gcloud config set project [PROJECT ID]
    ```
8.  In the file editor open up the
    `ads-policy-monitor/terraform/example.tfvars`, and update the variables with
    your configuration (including credentials obtained from Steps 3 and 4).
9.  Run the deployment script in the `Terminal`: 
    ```
    sh init.sh
    ```

Done! Follow the link generated by the deployment script to get your copy of the
dashboard. Note: Access to this link is enabled only to users who are part of
[ads-policy-monitor-template-readers](https://groups.google.com/g/ads-policy-monitor-template-readers)
group as stated in the Requirements section.

Please note, the solution is scheduled to run at midnight each day. We recommend
waiting for the next day to see the data populated in the dashboard.
Alternatively you can force run the job in Cloud Scheduler. However this can
create duplicated data if you run more than once a day.
![Force run Cloud Scheduler screenshot](./docs/images/force-run-cloud-scheduler.png)

## FAQ

### Which Google Cloud APIs will be enabled to my project?

- Big Query API `bigquery.googleapis.com`
- Cloud Build `cloudbuild.googleapis.com`
- Cloud Funtions `cloudfunctions.googleapis.com`
- Cloud Resource Manager API `cloudresourcemanager.googleapis.com`
- Google Ads API `googleads.googleapis.com`
- Identity and Access Management (IAM) `iam.googleapis.com`
- Secret Manager `secretmanager.googleapis.com`
- Cloud Run `run.googleapis.com`
- Cloud Scheduler `cloudscheduler.googleapis.com`

You can also check this on the deployment file [ads-policy-monitor/init.sh](https://github.com/google-marketing-solutions/ads-policy-monitor/blob/main/init.sh#L78-L87).

### Which GAQL queries are executed?
Please refer to the folder google_ads_queries [cloud_functions/ads_policy_monitor/gaql](https://github.com/google-marketing-solutions/ads-policy-monitor/tree/main/cloud_functions/ads_policy_monitor/gaql).


### Can I deploy it in an existing Cloud Project or do I need to create a new one just for this solution?
You can use an existing Project if you want to. However, please remember that the best practice for clients is to create a new project dedicated to this solution (or any new solution).

### Can this solution refresh the data more often than once a day?
You can make the Cloud Scheduler run more often than once a day, however you'd need to also make some customization in the code as the code and templates provided here would show duplicated records.

The reason this solution was designed to run once a day was based on learnings from hundreds of deployments, where the tradeoff between solution costs and Policy Reviews turn-around time was taken into consideration.

If youy still wish to make the refresh rate higher, these are some of the adjustments you'd have to perform:
1. Introduce time into the [`event_date`](https://github.com/google-marketing-solutions/ads-policy-monitor/blob/main/cloud_functions/ads_policy_monitor/gaql/ad_policy_data.sql#L15) parameter of the queries.
2. Update the [cron schedule](https://github.com/google-marketing-solutions/ads-policy-monitor/blob/main/terraform/main.tf#L264) to run more frequently.
3. Update the [partitioning on the BigQuery table](https://github.com/google-marketing-solutions/ads-policy-monitor/blob/main/terraform/main.tf#L48) to hourly.
4. Update the [latestadpolicy data query](https://github.com/google-marketing-solutions/ads-policy-monitor/blob/main/bigquery/views/latest_ad_policy_data.sql#L37) to filter on only the latest data.
5. Refresh your Looker Studio dashboard data source to mke sure the `event_date` is now a datetime and instead of just date.


## Contributing

### Code formatting

The code is formatted using [yapf](https://github.com/google/yapf). After making
a change, before submitting the code please do the following:

Install the dev requirements:
```
pip install -r requirements_dev.txt
```

Then run yapf:

```
yapf --style google -r -i .
```

## Disclaimers
__This is not an officially supported Google product.__

Copyright 2024 Google LLC. This solution, including any related sample code or
data, is made available on an “as is,” “as available,” and “with all faults”
basis, solely for illustrative purposes, and without warranty or representation
of any kind. This solution is experimental, unsupported and provided solely for
your convenience. Your use of it is subject to your agreements with Google, as
applicable, and may constitute a beta feature as defined under those agreements.
To the extent that you make any data available to Google in connection with your
use of the solution, you represent and warrant that you have all necessary and
appropriate rights, consents and permissions to permit Google to use and process
that data. By using any portion of this solution, you acknowledge, assume and
accept all risks, known and unknown, associated with its usage, including with
respect to your deployment of any portion of this solution in your systems, or
usage in connection with your business, if at all.
