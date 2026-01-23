import boto3
from src.decorators import handle_aws_errors, log_execution_time


class EC2Manager:
    def __init__(self, session=None):
        self.session = session if session else boto3.Session()
        self.main_client = self.session.client('ec2', region_name='us-east-1')

    @handle_aws_errors
    def get_all_regions(self):
        response = self.main_client.describe_regions()
        regions = [r['RegionName'] for r in response['Regions']]
        return regions
    
    @log_execution_time
    def get_running_instances(self, region, tag_key, tag_value):
        ec2 = self.session.client('ec2', region_name=region)
        paginator = ec2.get_paginator('describe_instances')

        page_iterator = paginator.paginate(
            Filters = [
                {'Name': f'tag:{tag_key}', 'Values': [tag_value]},
                {'Name': 'instance-state-name', 'Values': ['running']}
            ]
        )
        for page in page_iterator:
            for reservation in page['Reservations']:
                for instance in reservation['Instances']:
                    yield instance['InstanceID']

    @handle_aws_errors
    def stop_instances(self, region, instance_ids):
        if not instance_ids:
            return
        
        ec2 = self.session.client('ec2', region_name=region)
        ec2.stop_instances(InstanceIds=instance_ids)
        print(f"Stopped {len(instance_ids)} instances in {region}: {instance_ids}")