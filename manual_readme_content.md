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
