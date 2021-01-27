# --
# File: awssts_consts.py
#
# Copyright (c) 2021 Splunk Inc.
#
# SPLUNK CONFIDENTIAL - Use or disclosure of this material in whole or in part
# without a valid written license from Splunk Inc. is PROHIBITED.
#
# --

STS_JSON_ACCESS_KEY = "access_key"
STS_JSON_SECRET_KEY = "secret_key"

STS_REGION_DICT = {
        "US East (Ohio)": "us-east-1",
        "US East (N. Virginia)": "us-east-2",
        "US West (N. California)": "us-west-1",
        "US West (Oregon)": "us-west-2",
        "Canada (Central)": "ca-central-1",
        "Asia Pacific (Mumbai)": "ap-south-1",
        "Asia Pacific (Tokyo)": "ap-northeast-1",
        "Asia Pacific (Seoul)": "ap-northeast-2",
        "Asia Pacific (Singapore)": "ap-southeast-1",
        "Asia Pacific (Sydney)": "ap-southeast-2",
        "China (Ningxia)": "cn-northwest-1",
        "EU (Frankfurt)": "eu-central-1",
        "EU (Ireland)": "eu-west-1",
        "EU (London)": "eu-west-2",
        "South Americia (Sao Paulo)": "sa-east-1",
        "US GovCloud East": "us-gov-east-1",
        "US GovCloud West": "us-gov-west-1",
    }

DEFAULT_ROLE_SESSION_DURATION = 3600
DEFAULT_ROLE_SESSION_NAME = 'Request_from_Phantom'
ASSUME_ROLE_SUCCESS_MSG = 'Successfully retrieved assume role credentials from region {}'
ASSUME_ROLE_CREDENTIALS_FAILURE_MSG = 'Failed to retrieve EC2 role credentials'
ASSUME_ROLE_BAD_ASSET_CONFIG_MSG = 'Please provide access keys or select assume role check box in asset configuration'
