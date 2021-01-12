# --
# File: awssts_connector.py
#
# Copyright (c) 2020 Splunk Inc.
#
# SPLUNK CONFIDENTIAL - Use or disclosure of this material in whole or in part
# without a valid written license from Splunk Inc. is PROHIBITED.
#
# --

# Phantom App imports
import phantom.app as phantom
from phantom.base_connector import BaseConnector
from phantom.action_result import ActionResult

# Usage of the consts file is recommended
from awssts_consts import *
from boto3 import client, Session
from datetime import datetime
from botocore.config import Config
import requests
import json
import six


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
        except:
            pass

        if isinstance(cur_obj, dict):
            new_dict = {}
            for k, v in six.iteritems(cur_obj):
                new_dict[k] = self._sanitize_dates(v)
            return new_dict

        if isinstance(cur_obj, list):
            new_list = []
            for v in cur_obj:
                new_list.append(self._sanitize_dates(v))
            return new_list

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
        external_id = param.get('external_id', None)
        role_arn = param.get('role_arn', None)
        role_session_duration = param.get('role_session_duration',
                                          DEFAULT_ROLE_SESSION_DURATION)

        # create client
        if phantom.is_fail(self._create_client(action_result, service='sts', new_region=param.get('region'))):
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

        return action_result.set_status(phantom.APP_SUCCESS, ASSUME_ROLE_SUCCESS_MSG)

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
    import pudb
    import argparse

    pudb.set_trace()

    argparser = argparse.ArgumentParser()

    argparser.add_argument('input_test_json', help='Input Test JSON file')
    argparser.add_argument('-u', '--username', help='username', required=False)
    argparser.add_argument('-p', '--password', help='password', required=False)

    args = argparser.parse_args()
    session_id = None

    username = args.username
    password = args.password

    if username is not None and password is None:

        # User specified a username but not a password, so ask
        import getpass
        password = getpass.getpass("Password: ")

    if username and password:
        try:
            login_url = AwsSecureTokenServiceConnector._get_phantom_base_url() + '/login'

            print("Accessing the Login page")
            r = requests.get(login_url, verify=False)
            csrftoken = r.cookies['csrftoken']

            data = dict()
            data['username'] = username
            data['password'] = password
            data['csrfmiddlewaretoken'] = csrftoken

            headers = dict()
            headers['Cookie'] = 'csrftoken=' + csrftoken
            headers['Referer'] = login_url

            print("Logging into Platform to get the session id")
            r2 = requests.post(login_url, verify=False, data=data, headers=headers)
            session_id = r2.cookies['sessionid']
        except Exception as e:
            print("Unable to get session id from the platform. Error: " + str(e))
            exit(1)

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

    exit(0)


if __name__ == '__main__':
    main()
