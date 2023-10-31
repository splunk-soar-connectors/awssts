# File: awssts_connector.py
#
# Copyright (c) 2021-2023 Splunk Inc.
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#     http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software distributed under
# the License is distributed on an "AS IS" BASIS, WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND,
# either express or implied. See the License for the specific language governing permissions
# and limitations under the License.
#
#
import json
from datetime import datetime

import phantom.app as phantom
import requests
from boto3 import Session, client
from botocore.config import Config
from phantom.action_result import ActionResult
from phantom.base_connector import BaseConnector

from awssts_consts import *


class RetVal(tuple):

    def __new__(cls, val1, val2=None):
        return tuple.__new__(RetVal, (val1, val2))


class AwsSecureTokenServiceConnector(BaseConnector):

    def __init__(self):

        # Call the BaseConnectors init first
        super(AwsSecureTokenServiceConnector, self).__init__()

        self._state = None
        self._region = None
        self._access_key = None
        self._secret_key = None
        self._token = None
        self._proxy = None

    def initialize(self):
        self._state = self.load_state()

        config = self.get_config()

        self._region = STS_REGION_DICT.get(config['region'])
        if not self._region:
            return self.set_status(phantom.APP_ERROR, "Specified region is not valid")

        self._proxy = {}
        env_vars = config.get('_reserve_environment_variables', {})
        if 'HTTP_PROXY' in env_vars:
            self._proxy['http'] = env_vars['HTTP_PROXY']['value']
        if 'HTTPS_PROXY' in env_vars:
            self._proxy['https'] = env_vars['HTTPS_PROXY']['value']

        # Check for EC2 role creds, otherwise use the ones in the config
        if config.get('use_role'):
            credentials = self._handle_get_ec2_role()
            if not credentials:
                return self.set_status(phantom.APP_ERROR, ASSUME_ROLE_CREDENTIALS_FAILURE_MSG)
            self._access_key = credentials.access_key
            self._secret_key = credentials.secret_key
            self._token = credentials.token

            return phantom.APP_SUCCESS

        self._access_key = config.get(STS_JSON_ACCESS_KEY)
        self._secret_key = config.get(STS_JSON_SECRET_KEY)

        if not (self._access_key and self._secret_key):
            return self.set_status(phantom.APP_ERROR, ASSUME_ROLE_BAD_ASSET_CONFIG_MSG)

        return phantom.APP_SUCCESS

    def finalize(self):
        self.save_state(self._state)

        return phantom.APP_SUCCESS

    def _create_client(self, action_result, service='sts', new_region=None):

        boto_config = None
        if self._proxy:
            boto_config = Config(proxies=self._proxy)

        if new_region:
            self._region = STS_REGION_DICT.get(new_region)

        try:
            if self._access_key and self._secret_key:
                self.debug_print("Creating boto3 client with API keys")

                self._client = client(
                    service,
                    region_name=self._region,
                    aws_access_key_id=self._access_key,
                    aws_secret_access_key=self._secret_key,
                    aws_session_token=self._token,
                    config=boto_config
                )

            else:
                self.debug_print("Creating boto3 client without API keys")

                self._client = client(
                    'sts',
                    region_name=self._region,
                    config=boto_config
                )
        except Exception as e:
            return action_result.set_status(phantom.APP_ERROR, "Could not create boto3 client: {0}".format(e))

        return phantom.APP_SUCCESS

    def _sanitize_dates(self, cur_obj):

        try:
            json.dumps(cur_obj)
            return cur_obj
        except Exception:
            pass

        if isinstance(cur_obj, dict):
            return {k: self._sanitize_dates(v) for k, v in cur_obj.items()}

        if isinstance(cur_obj, list):
            return [self._sanitize_dates(v) for v in cur_obj]

        if isinstance(cur_obj, datetime):
            return cur_obj.strftime("%Y-%m-%d %H:%M:%S")

        return cur_obj

    def _make_boto_call(self, action_result, method, **kwargs):

        try:
            boto_func = getattr(self._client, method)
        except AttributeError:
            return RetVal(action_result.set_status(phantom.APP_ERROR, "Invalid method: {0}".format(method)), None)

        try:
            resp_json = boto_func(**kwargs)
        except Exception as e:
            return RetVal(action_result.set_status(phantom.APP_ERROR, "boto3 call to STS failed", e), None)

        return phantom.APP_SUCCESS, self._sanitize_dates(resp_json)

    def _handle_test_connectivity(self, param):

        self.save_progress("Querying STS to check credentials")
        action_result = self.add_action_result(ActionResult(dict(param)))

        if not self._create_client(action_result):
            return action_result.get_status()

        ret_val, resp_json = self._make_boto_call(action_result, 'get_caller_identity')

        if phantom.is_fail(ret_val):
            self.save_progress("Test Connectivity Failed.")
            return ret_val

        self.save_progress("Test Connectivity Passed")
        return action_result.set_status(phantom.APP_SUCCESS)

    def _handle_assume_role(self, param):

        self.save_progress("In action handler for: {0}".format(self.get_action_identifier()))

        action_result = self.add_action_result(ActionResult(dict(param)))

        role_session_name = param.get('role_session_name',
                                      DEFAULT_ROLE_SESSION_NAME)
        external_id = param.get('external_id')
        role_arn = param.get('role_arn')
        role_session_duration = param.get('role_session_duration',
                                          DEFAULT_ROLE_SESSION_DURATION)
        region = param.get('region')
        if not region:
            region = self._region
            for region_name, region_value in STS_REGION_DICT.items():
                if region_value == region:
                    region = region_name

        # create client
        if phantom.is_fail(self._create_client(action_result, service='sts', new_region=region)):
            return action_result.get_status()

        # make boto3 call
        if external_id:
            ret_val, resp_json = self._make_boto_call(action_result, 'assume_role',
                                                      RoleSessionName=role_session_name,
                                                      RoleArn=role_arn,
                                                      ExternalId=external_id,
                                                      DurationSeconds=role_session_duration)
        else:
            ret_val, resp_json = self._make_boto_call(action_result, 'assume_role',
                                                      RoleSessionName=role_session_name,
                                                      RoleArn=role_arn,
                                                      DurationSeconds=role_session_duration)
        if phantom.is_fail(ret_val):
            return action_result.get_status()

        action_result.add_data(resp_json)

        self.save_progress(f"Action handler for: {self.get_action_identifier()} has finished successfully")

        return action_result.set_status(phantom.APP_SUCCESS, ASSUME_ROLE_SUCCESS_MSG.format(region))

    def handle_action(self, param):
        ret_val = phantom.APP_SUCCESS

        # Get the action that we are supposed to execute for this App Run
        action_id = self.get_action_identifier()

        self.debug_print("action_id", self.get_action_identifier())

        if action_id == 'test_connectivity':
            ret_val = self._handle_test_connectivity(param)

        elif action_id == 'assume_role':
            ret_val = self._handle_assume_role(param)

        return ret_val

    def _handle_get_ec2_role(self):

        session = Session(region_name=self._region)
        credentials = session.get_credentials()
        return credentials


def main():
    import argparse
    import sys

    import pudb

    pudb.set_trace()

    argparser = argparse.ArgumentParser()

    argparser.add_argument('input_test_json', help='Input Test JSON file')
    argparser.add_argument('-u', '--username', help='username', required=False)
    argparser.add_argument('-p', '--password', help='password', required=False)
    argparser.add_argument('-v', '--verify', action='store_true', help='verify', required=False, default=False)

    args = argparser.parse_args()
    session_id = None

    username = args.username
    password = args.password
    verify = args.verify

    if username is not None and password is None:

        # User specified a username but not a password, so ask
        import getpass
        password = getpass.getpass("Password: ")

    if username and password:
        try:
            login_url = AwsSecureTokenServiceConnector._get_phantom_base_url() + '/login'

            print("Accessing the Login page")
            r = requests.get(login_url, verify=verify, timeout=DEFAULT_TIMEOUT)
            csrftoken = r.cookies['csrftoken']

            data = dict()
            data['username'] = username
            data['password'] = password
            data['csrfmiddlewaretoken'] = csrftoken

            headers = dict()
            headers['Cookie'] = 'csrftoken=' + csrftoken
            headers['Referer'] = login_url

            print("Logging into Platform to get the session id")
            r2 = requests.post(login_url, verify=verify, data=data, headers=headers, timeout=DEFAULT_TIMEOUT)
            session_id = r2.cookies['sessionid']
        except Exception as e:
            print("Unable to get session id from the platform. Error: " + str(e))
            sys.exit(1)

    with open(args.input_test_json) as f:
        in_json = f.read()
        in_json = json.loads(in_json)
        print(json.dumps(in_json, indent=4))

        connector = AwsSecureTokenServiceConnector()
        connector.print_progress_message = True

        if session_id is not None:
            in_json['user_session_token'] = session_id
            connector._set_csrf_info(csrftoken, headers['Referer'])

        ret_val = connector._handle_action(json.dumps(in_json), None)
        print(json.dumps(json.loads(ret_val), indent=4))

    sys.exit(0)


if __name__ == '__main__':
    main()
