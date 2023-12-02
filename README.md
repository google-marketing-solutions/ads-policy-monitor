# Ads Policy Monitor

_Providing a 1-stop-shop, centralized view of all your Google Ads policy
reports._

Ads Policy Monitor provides a data pipeline for pulling ad approval data from
Google Ads, enabling you to monitor trends and spikes with ad approvals.

## Deployment

The code is deployed using [Terraform](https://www.terraform.io/).

### Manual Steps

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
