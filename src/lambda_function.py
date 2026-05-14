from concurrent.futures import ThreadPoolExecutor
from datetime import datetime, timezone
import json
import os
import logging
import boto3
from src.ec2_manager import EC2Manager


logger = logging.getLogger()
logger.setLevel(logging.INFO)

TAG_KEY = os.environ.get('TAG_KEY', 'Environment')
TAG_VALUE = os.environ.get('TAG_VALUE', 'Dev')
SNS_TOPIC_ARN = os.environ.get('SNS_TOPIC_ARN')
S3_BUCKET_NAME = os.environ.get('S3_BUCKET_NAME')

sns_client = boto3.client('sns')
s3_client = boto3.client('s3')


def process_region(region):
    manager = EC2Manager()
    instance_ids = list(manager.get_running_instances(region, TAG_KEY, TAG_VALUE))

    if instance_ids:
        logger.info(f"Region {region}: Found {len(instance_ids)} instances.")
        manager.stop_instances(region, instance_ids)

        if SNS_TOPIC_ARN:
            sns_client.publish(
                TopicArn=SNS_TOPIC_ARN,
                Message=(
                    f"Cost Sentinel: Stopped {len(instance_ids)} instances "
                    f"in {region} ({', '.join(instance_ids)})"
                ),
            )

    return {"region": region, "instance_ids": instance_ids}


def lambda_handler(event, context):
    manager = EC2Manager()
    regions = manager.get_all_regions()

    with ThreadPoolExecutor(max_workers=10) as executor:
        results = list(executor.map(process_region, regions))

    timestamp = datetime.now(timezone.utc).isoformat()
    stopped_by_region = {
        r["region"]: r["instance_ids"] for r in results if r["instance_ids"]
    }
    clean_regions = [r["region"] for r in results if not r["instance_ids"]]
    total_stopped = sum(len(ids) for ids in stopped_by_region.values())

    summary = {
        "timestamp": timestamp,
        "total_stopped": total_stopped,
        "regions": stopped_by_region,
        "regions_clean": clean_regions,
    }

    if S3_BUCKET_NAME:
        s3_client.put_object(
            Bucket=S3_BUCKET_NAME,
            Key=f"reports/{timestamp}.json",
            Body=json.dumps(summary),
            ContentType="application/json",
        )

    logger.info(f"Execution Complete. Summary: {summary}")
    return {"statusCode": 200, "body": json.dumps(summary)}
