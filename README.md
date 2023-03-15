# POC: Shelly Cloud Control API - WebSocket API

Forked from [corenting/poc_shelly_cloud_control_api_ws](https://github.com/corenting/poc_shelly_cloud_control_api_ws).

A quick & small POC in Python on how to use the [Shelly Cloud Control API](https://shelly-api-docs.shelly.cloud/cloud-control-api/real-time-events#websocket-api) (and more specifically the WebSocket API) to get data from a Shelly device (tested with a Shelly Plug S).

The aim is to get realtime data (temperature, power in watts) from the device directly from the Shelly Cloud, like [the official Shelly Home website](https://home.shelly.cloud/#/login), which seems to use the same API to display realtime data.

⚠️ **This is not a complete program, it was used as a POC to try to understand how the Cloud Control API worked and how the OAuth connection flow could be automated as the official documentation is lacking examples.
It doesn't have any error management, access token expiration handling, security etc.**

## How to use

Once the setup is done, the `poc.py` file will try to get OAuth credentials and fetch events through the WebSocket API. As it doesn't handle OAuth session management it will probably crash once the access token expires.

You need to:
1. In your Python environments, install the dependencies: `pipenv install`
2. Run it:
```bash
pipenv run python3 poc.py -u <your_shelly_cloud_email> -p <your_shelly_cloud_password> -s <your_shelly_server>
```