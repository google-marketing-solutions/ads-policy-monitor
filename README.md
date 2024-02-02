# Ads Policy Monitor

_Providing a 1-stop-shop, centralized view of all your Google Ads policy
reports._

Ads Policy Monitor provides a data pipeline for pulling ad and asset approval data from Google Ads, enabling you to monitor trends and spikes with policy approvals.

## Solution Overview

To keep ads safe and appropriate for everyone, ads are reviewed to make sure
they comply with Google Ads policies, [read more here](
https://support.google.com/google-ads/answer/1722120?sjid=13030684844768437853-EU).

For large advertisers and agencies, it can be challenging to monitor the state
of your ad copy across all of your Google Ads accounts. This can be amplified
when automation is used to create ad copy, as it's easy to introduce mistakes
that result in ads being disapproved, for example, the incorrect use of
capitalisation.

This solution pulls a daily snapshot of your ad and asset policy approvals, stores them in BigQuery, and provides a Looker Studio dashboard template to monitor this.

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

1. A daily cron job runs that makes a HTTPS request to trigger the
   `ads_policy_monitor` Cloud Function.
2. The Cloud Function uses [Google Ads Query Language (GAQL)](
   https://developers.google.com/google-ads/api/docs/query/overview) to run a
   number of reports in Google Ads via the API.
3. The output of these reports is written to a dataset in BigQuery called
   `ads_policy_monitor`.
4. We provide a template Looker Studio dashboard to visualise this data.
   However, there is nothing to stop you using your own dashboard solution. For
   example, it is possible to connect this data with the Looker Platform for
   more advanced BI reporting, alerting, data drilldown etc.

## Requirements

- A Google Cloud Project
- Access to the Google Ads API (e.g. developer token, account access), [see
  getting started](https://developers.google.com/google-ads/api/docs/get-started/introduction).
- Access to Looker Studio or a dashboard solution that can connect to BigQuery.
  - If you wish to have access to the [Looker Studio template provided by Google](https://lookerstudio.google.com/c/u/0/reporting/13995d1f-741c-40f0-934c-9517e2ffc361/), please join this group [ads-policy-monitor-template-readers](https://groups.google.com/g/ads-policy-monitor-template-readers).

## Deployment

1. Open the Google Cloud Project in the UI.
2. Open the [OAuth Consent Screen](
   https://console.cloud.google.com/apis/credentials/consent) and create a new
   internal app.
3. Open the [API Credentials Screen](
   https://console.cloud.google.com/apis/credentials) -> Create credentials ->
   OAuth Client ID -> Web app -> Set
   `https://developers.google.com/oauthplayground` as an authorised redirect
   URI. Make a note of the `client_id` and the `client_secret`.
4. Open the [OAuth playground](https://developers.google.com/oauthplayground/),
   and generate a refresh token for the following scopes, using the
   `client_id` and `client_secret` generated in the previous step:
   ```
   https://www.googleapis.com/auth/adwords
   ```
5. Open Cloud Shell
6. Clone the repo & open the directory with the code:
   ```
   git clone https://github.com/google-marketing-solutions/ads-policy-monitor.git
   ```
7. Go to `Terminal` -> `New Terminal` from the menu. 
   Make sure you're in the intended Cloud project. Otherwise, set the shell to use the
   correct cloud project:
   ```
   gcloud config set project [PROJECT ID]
   ```
8. In the file editor open up the `ads-policy-monitor/terraform/example.tfvars`,
and update the variables with your configuration (including credentials obtained from Steps 3 and 4).
9. Run the deployment script in the `Terminal`:
   ```
   sh init.sh
   ```

Done! Follow the link generated by the deployment script to get your copy of the dashboard.

Please note, the solution is scheduled to run at midnight each day. We recommend waiting for the next day to see the data populated in the dashboard. Alternatively you can force run the job in Cloud Scheduler, however this can create duplicated data.

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
