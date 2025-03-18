# AWS Security Token Service

Publisher: Splunk \
Connector Version: 1.2.11 \
Product Vendor: AWS \
Product Name: Security Token Service \
Minimum Product Version: 6.3.0

This app integrates with AWS Security Token Service and allows a user to retrieve a temporary set of credentials for some specified account

## Asset Configuration

There are two ways to configure an AWS STS asset. The first is to configure the **access_key** ,
**secret_key** and **region** variables. If it is preferred to use a role and Phantom is running as
an EC2 instance, the **use_role** checkbox can be checked instead. This will allow the role that is
attached to the instance to be used. Please see the [AWS EC2 and IAM
documentation](https://docs.aws.amazon.com/AWSEC2/latest/UserGuide/iam-roles-for-amazon-ec2.html)
for more information.

## Assuming a Role

When calling the **assume_role** action, a dictionary containing the **AccessKeyId** ,
**SecretAccessKey** , **SessionToken** and **Expiration** key/value pairs with data path
**assume_role_1:action_result.data.\*.Credentials** will be returned. This dictionary can be passed
directly into the **credentials** parameter in another AWS app's action within a playbook. These
credentials will be used to override the asset configuration of that app when executing the action.
This is true whether the receiving action's asset is configured with the access key and secret key
or if the EC2 instance role credentials are used.

### Configuration variables

This table lists the configuration variables required to operate AWS Security Token Service. These variables are specified when configuring a Security Token Service asset in Splunk SOAR.

VARIABLE | REQUIRED | TYPE | DESCRIPTION
-------- | -------- | ---- | -----------
**access_key** | optional | password | Access Key |
**secret_key** | optional | password | Secret Key |
**region** | required | string | Default Region |
**use_role** | optional | boolean | Use attached role when running Phantom in EC2 |

### Supported Actions

[test connectivity](#action-test-connectivity) - Validate the asset configuration for connectivity using supplied configuration \
[assume role](#action-assume-role) - Assume a role

## action: 'test connectivity'

Validate the asset configuration for connectivity using supplied configuration

Type: **test** \
Read only: **True**

#### Action Parameters

No parameters are required for this action

#### Action Output

No Output

## action: 'assume role'

Assume a role

Type: **generic** \
Read only: **False**

Retrieve a token for a specified role and user account.

#### Action Parameters

PARAMETER | REQUIRED | DESCRIPTION | TYPE | CONTAINS
--------- | -------- | ----------- | ---- | --------
**role_arn** | required | Role ARN | string | `aws role arn` |
**role_session_name** | required | Role Session Name | string | `aws role session name` |
**role_session_duration** | optional | Role Session Duration (Seconds) | numeric | |
**external_id** | optional | External ID | string | `aws external id` |
**region** | optional | Region, overrides default region in asset configuration | string | |

#### Action Output

DATA PATH | TYPE | CONTAINS | EXAMPLE VALUES
--------- | ---- | -------- | --------------
action_result.parameter.role_session_name | string | `aws role session name` | Request_from_Phantom |
action_result.parameter.external_id | string | `aws external id` | 999 |
action_result.parameter.role_arn | string | `aws role arn` | arn:aws:iam::157568069999:role/TestRole |
action_result.status | string | | success failed |
action_result.message | string | | Successfully retrieved assume role credentials boto3 call to STS failed. Error string: 'An error occurred (AccessDenied) when calling the AssumeRole operation: User: arn:aws:iam::999999999999:user/test-user is not authorized to perform: sts:AssumeRole on resource: arn:aws:iam::888888888888:role/TestRole' |
action_result.data.\*.Credentials | string | `aws credentials` | {'AccessKeyId': '\*REDACTED\*', 'SecretAccessKey': '\*REDACTED\*', 'SessionToken': '\*REDACTED\*', 'Expiration': '2020-11-16 21:49:35'} |
action_result.data.\*.Credentials.Expiration | string | | 2020-12-03 21:59:19 |
action_result.data.\*.Credentials.AccessKeyId | string | | \*REDACTED\* |
action_result.data.\*.Credentials.SessionToken | string | | \*REDACTED\* |
action_result.data.\*.Credentials.SecretAccessKey | string | | \*REDACTED\* |
action_result.data.\*.AssumedRoleUser.Arn | string | | arn:aws:sts::157568099999:assumed-role/TestRole/Request_from_Phantom |
action_result.data.\*.AssumedRoleUser.AssumedRoleId | string | | \*REDACTED\* |
action_result.data.\*.ResponseMetadata.RequestId | string | | c8bc1c72-36e1-4b27-8f28-95e26e7013ea |
action_result.data.\*.ResponseMetadata.HTTPHeaders.date | string | | Thu, 03 Dec 2020 20:59:19 GMT |
action_result.data.\*.ResponseMetadata.HTTPHeaders.content-type | string | | text/xml |
action_result.data.\*.ResponseMetadata.HTTPHeaders.content-length | string | | 1073 |
action_result.data.\*.ResponseMetadata.HTTPHeaders.x-amzn-requestid | string | | c8bc1c72-36e1-4b27-8f28-95e26e7013ea |
action_result.data.\*.ResponseMetadata.RetryAttempts | numeric | | 0 |
action_result.data.\*.ResponseMetadata.HTTPStatusCode | numeric | | 200 |
action_result.parameter.role_session_duration | numeric | | 3600 |
action_result.parameter.region | string | | US East (Ohio) |
action_result.summary | string | | |
summary.total_objects | numeric | | 1 |
summary.total_objects_successful | numeric | | 0 |

______________________________________________________________________

Auto-generated Splunk SOAR Connector documentation.

Copyright 2025 Splunk Inc.

Licensed under the Apache License, Version 2.0 (the "License");
you may not use this file except in compliance with the License.
You may obtain a copy of the License at

http://www.apache.org/licenses/LICENSE-2.0

Unless required by applicable law or agreed to in writing,
software distributed under the License is distributed on an "AS IS" BASIS,
WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
See the License for the specific language governing permissions and limitations under the License.
