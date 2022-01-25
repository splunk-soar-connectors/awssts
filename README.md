[comment]: # "Auto-generated SOAR connector documentation"
# AWS Security Token Service

Publisher: Splunk  
Connector Version: 1\.2\.9  
Product Vendor: AWS  
Product Name: Security Token Service  
Product Version Supported (regex): "\.\*"  
Minimum Product Version: 4\.10\.0\.40961  

This app integrates with AWS Security Token Service and allows a user to retrieve a temporary set of credentials for some specified account

[comment]: # " File: README.md"
[comment]: # "  Copyright (c) 2021-2022 Splunk Inc."
[comment]: # ""
[comment]: # "Licensed under the Apache License, Version 2.0 (the 'License');"
[comment]: # "you may not use this file except in compliance with the License."
[comment]: # "You may obtain a copy of the License at"
[comment]: # ""
[comment]: # "    http://www.apache.org/licenses/LICENSE-2.0"
[comment]: # ""
[comment]: # "Unless required by applicable law or agreed to in writing, software distributed under"
[comment]: # "the License is distributed on an 'AS IS' BASIS, WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND,"
[comment]: # "either express or implied. See the License for the specific language governing permissions"
[comment]: # "and limitations under the License."
[comment]: # ""
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


### Configuration Variables
The below configuration variables are required for this Connector to operate.  These variables are specified when configuring a Security Token Service asset in SOAR.

VARIABLE | REQUIRED | TYPE | DESCRIPTION
-------- | -------- | ---- | -----------
**access\_key** |  optional  | password | Access Key
**secret\_key** |  optional  | password | Secret Key
**region** |  required  | string | Default Region
**use\_role** |  optional  | boolean | Use attached role when running Phantom in EC2

### Supported Actions  
[test connectivity](#action-test-connectivity) - Validate the asset configuration for connectivity using supplied configuration  
[assume role](#action-assume-role) - Assume a role  

## action: 'test connectivity'
Validate the asset configuration for connectivity using supplied configuration

Type: **test**  
Read only: **True**

#### Action Parameters
No parameters are required for this action

#### Action Output
No Output  

## action: 'assume role'
Assume a role

Type: **generic**  
Read only: **False**

Retrieve a token for a specified role and user account\.

#### Action Parameters
PARAMETER | REQUIRED | DESCRIPTION | TYPE | CONTAINS
--------- | -------- | ----------- | ---- | --------
**role\_arn** |  required  | Role ARN | string |  `aws role arn` 
**role\_session\_name** |  required  | Role Session Name | string |  `aws role session name` 
**role\_session\_duration** |  optional  | Role Session Duration \(Seconds\) | numeric | 
**external\_id** |  optional  | External ID | string |  `aws external id` 
**region** |  optional  | Region, overrides default region in asset configuration | string | 

#### Action Output
DATA PATH | TYPE | CONTAINS
--------- | ---- | --------
action\_result\.parameter\.role\_session\_name | string |  `aws role session name` 
action\_result\.parameter\.external\_id | string |  `aws external id` 
action\_result\.parameter\.role\_arn | string |  `aws role arn` 
action\_result\.status | string | 
action\_result\.message | string | 
action\_result\.data\.\*\.Credentials | string |  `aws credentials` 
action\_result\.data\.\*\.Credentials\.Expiration | string | 
action\_result\.data\.\*\.Credentials\.AccessKeyId | string | 
action\_result\.data\.\*\.Credentials\.SessionToken | string | 
action\_result\.data\.\*\.Credentials\.SecretAccessKey | string | 
action\_result\.data\.\*\.AssumedRoleUser\.Arn | string | 
action\_result\.data\.\*\.AssumedRoleUser\.AssumedRoleId | string | 
action\_result\.data\.\*\.ResponseMetadata\.RequestId | string | 
action\_result\.data\.\*\.ResponseMetadata\.HTTPHeaders\.date | string | 
action\_result\.data\.\*\.ResponseMetadata\.HTTPHeaders\.content\-type | string | 
action\_result\.data\.\*\.ResponseMetadata\.HTTPHeaders\.content\-length | string | 
action\_result\.data\.\*\.ResponseMetadata\.HTTPHeaders\.x\-amzn\-requestid | string | 
action\_result\.data\.\*\.ResponseMetadata\.RetryAttempts | numeric | 
action\_result\.data\.\*\.ResponseMetadata\.HTTPStatusCode | numeric | 
action\_result\.parameter\.role\_session\_duration | numeric | 
action\_result\.parameter\.region | string | 
action\_result\.summary | string | 
summary\.total\_objects | numeric | 
summary\.total\_objects\_successful | numeric | 