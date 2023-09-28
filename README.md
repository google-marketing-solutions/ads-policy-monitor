# Ads Policy Monitor

_Providing a 1-stop-shop, centralized view of all your Google Ads policy
reports._

Ads Policy Monitor provides a data pipeline for pulling ad approval data from
Google Ads, enabling you to monitor trends and spikes with ad approvals.

## Deployment

The code is deployed using [Terraform](https://www.terraform.io/).

Open [Cloud Shell in Google Cloud](
  https://console.cloud.google.com/cloudshelleditor?cloudshell=true).

Clone the repo:
```
git clone https://github.com/google-marketing-solutions/ads-policy-monitor.git
```

Press the open shell editor button.

Go to `Terminal` -> `New Terminal` from the menu.

Set the shell to use the correct cloud project:

```
gcloud config set project [PROJECT ID]
```

Enable the APIs:

```
gcloud services enable \
   bigquery.googleapis.com \
   cloudbuild.googleapis.com \
   cloudfunctions.googleapis.com \
   cloudresourcemanager.googleapis.com \
   googleads.googleapis.com \
   iam.googleapis.com
```

Then navigate into the terraform directory:

```
cd ads-policy-monitor/terraform
```

In the file editor open up the `ads-policy-monitor/terraform/terraform.tfvars`,
and update the variables with your configuration.

Back in the terminal session run:

```
terraform init
terraform apply --var-file terraform.tfvars
```

## Code formatting

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

Copyright 2023 Google LLC. This solution, including any related sample code or
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
