# Ads Policy Monitor Cloud Function

A Gen2 Cloud Function to get various reports from Google Ads in relation to ad
policy data.

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

## Running for a subset of reports

If you don't want to run all the reports, you can specify which reports to run
by providing a `reports_to_run` variable in the payload.

For example:

```
{
    "reports_to_run": ["OCID"],
    "project_id": "my_project",
    ...
}
```

