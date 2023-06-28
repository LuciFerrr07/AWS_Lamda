import json
import boto3
import time



client = boto3.client('ec2')
new_vol = []

def lambda_handler(event, context):
    # TODO implement
    vol=[];f=0; in_id = instance_id
    ec2 = boto3.resource('ec2', region_name='us-west-2')
    instance = ec2.Instance(in_id)
    volumes = instance.volumes.all()
    for v in volumes:
        vol.append(v.id)
    volume_info = client.describe_volumes(VolumeIds=vol) 
    res=volume_info['Volumes'][0]
    if res['Encrypted']==False:
        vol_id=res['Attachments'][0]['VolumeId']
        f=1
    if(f==1):
        stop_instance(in_id)
        r=client.describe_instances(InstanceIds=[in_id])
        status=r['Reservations'][0]['Instances'][0]['State']['Name']
        while(True):
            if(status == 'stopped'):
                break
            else:
                r=client.describe_instances(InstanceIds=[in_id])
                status=r['Reservations'][0]['Instances'][0]['State']['Name']
            
        detach_volume(in_id,vol_id)
        time.sleep(5)
        create_snapshot(vol_id)
        create_encrypted_volume(vol_id)
        time.sleep(5)
        attach_volume(in_id)
        start_instance(in_id)
        delete_detached_volume(vol_id)
    
    return {
        'statusCode': 200,
        'body': json.dumps('Hello from Lambda!')
    }
    
def stop_instance(id):
    response = client.stop_instances(InstanceIds=[id])
    return response
    
def detach_volume(in_id , v_id):
    response = client.detach_volume(InstanceId=in_id, VolumeId=v_id)
    return response
    
def create_snapshot(v_id):
    response = client.create_snapshot(VolumeId=v_id)
    return response
    
def create_encrypted_volume(v_id):
    s=client.describe_snapshots(Filters=[{'Name':'volume-id','Values':[v_id]}])
    snap_id = s['Snapshots'][0]['SnapshotId']
    state = s['Snapshots'][0]['State']
    while(1):
        if state == 'completed':
            break
        else:
            s=client.describe_snapshots(Filters=[{'Name':'volume-id','Values':[v_id]}])
            state = s['Snapshots'][0]['State']
            
    response = client.create_volume(
            SnapshotId = snap_id,
            AvailabilityZone='us-west-2a',
            VolumeType='gp3',
            Encrypted=True,
            KmsKeyId='alias/aws/ebs'     
        )
    return response
    
def attach_volume(in_id):
    res = client.describe_volumes()
    for i in res["Volumes"]:
        new_vol.append(i['VolumeId'])
    
    response = client.attach_volume(
        VolumeId = new_vol[-1],
        InstanceId = in_id, 
        Device='/dev/xvda'
    )
    return response

def start_instance(in_id):
    v = client.describe_volumes(VolumeIds=[new_vol[-1]])
    while(1):
        if v['Volumes'][0]['State']=='in-use':
            break
        else:
            v = client.describe_volumes(VolumeIds=[new_vol[-1]])
    response = client.start_instances(InstanceIds = [in_id])
    return response

def delete_detached_volume(v_id):
    response = client.delete_volume(VolumeId=v_id)
    return response
