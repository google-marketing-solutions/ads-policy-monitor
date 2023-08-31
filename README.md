# Policy Monitor Dashboard

Data pipeline for pulling ad approval data from Google Ads, enabling you to
monitor trends and spikes with ad approvals.

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
