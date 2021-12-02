[comment]: # " File: readme.md"
[comment]: # "  Copyright (c) 2021 Splunk Inc."
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
