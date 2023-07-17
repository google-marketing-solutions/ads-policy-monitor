# Keyword In Account

A Gen2 Cloud Function to get ad policy data from Google Ads.

## Deployment

Install the gcloud cli and set the right config then:

```
gcloud beta functions deploy get-ad-policy-data \
  --gen2 \
  --runtime=python311 \
  --region=europe-west2 \
  --source=. \
  --entry-point=main \
  --trigger-http \
  --memory=2048MB \
  --timeout=3600s
```

## Running locally
Set up the environment
```
python3 -m venv venv
source venv/bin/activate
pip install - requirements.txt
```

The code uses [Google Application Default credentials](
https://google-auth.readthedocs.io/en/master/reference/google.auth.html) for
auth.

First create OAuth desktop credentials in Google Cloud, and download the client
ID and client secret as a JSON file.

Then run the following command, updating the path to point to the JSON file
downloaded in the previous step:
```
gcloud auth application-default login \
  --scopes='https://www.googleapis.com/auth/cloud-platform' \
  --client-id-file=/path/to/client-id-file.json
```
[Optionally] [see this article](
https://medium.com/google-cloud/google-oauth-credential-going-deeper-the-hard-way-f403cf3edf9d)
for a detailed explanation, why this is needed.

Create a copy of the `example.json` and name it `secret.json`. Update this with
your secret credentials and run:

```
python main.py secret.json
```
