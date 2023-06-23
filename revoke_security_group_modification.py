import boto3
import json

def lambda_handler(event, context):
    ec2=boto3.client('ec2')
    #Retrieve the modified security group details from the event
    modified_security_group = event['detail']['requestParameters']['groupId']
    ip_permissions = event['detail']['requestParameters']['ipPermissions']['items']
    sg_rule=event['detail']['responseElements']['securityGroupRuleSet']['items']
    for i in sg_rule:
        if i['cidrIpv4']=='0.0.0.0/0':
            response = ec2.revoke_security_group_ingress(GroupId=modified_security_group, SecurityGroupRuleIds=[i['securityGroupRuleId']])
   
    return {
        'statusCode': 200,
        'body': 'Security group modification prevented successfully'
    }
