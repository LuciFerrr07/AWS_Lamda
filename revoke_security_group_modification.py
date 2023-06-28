import boto3
import json

def lambda_handler(event, context):
    ec2=boto3.client('ec2')
    event=json.loads(event['body'])
    res = event['result'].get('_raw');
    res = json.loads(res)
    modified_security_group = res['requestParameters']['groupId']
    sg_rule=res['responseElements']['securityGroupRuleSet']['items']
    for i in sg_rule:
        if i['cidrIpv4']=='0.0.0.0/0':
            response = ec2.revoke_security_group_ingress(GroupId=modified_security_group, SecurityGroupRuleIds=[i['securityGroupRuleId']])
   
    return {
        'statusCode': 200,
        'body': 'Security group modification prevented successfully'
    }
