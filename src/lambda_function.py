from concurrent.futures import ThreadPoolExecutor
import os
import logging
from src.ec2_manager import EC2Manager 


logger = logging.getLogger()
logger.setLevel(logging.INFO)

TAG_KEY = os.environ.get('TAG_KEY', 'Environment')
TAG_VALUE = os.environ.get('TAG_VALUE', 'Dev')

def process_region(region):
    manager = EC2Manager()
    instance_ids = list(manager.get_running_instances(region, TAG_KEY, TAG_VALUE))

    if instance_ids:
        logger.info(f"Region {region}: Found {len(instance_ids)} instances.")
        manager.stop_instances(region, instance_ids)

        return f"{region}: Stopped {len(instance_ids)}"
    
    return f"{region}: Clean"


def lambda_handler(event, context):
    manager = EC2Manager()
    regions = manager.get_all_regions()
    results = []

    with ThreadPoolExecutor(max_workers=10) as executor:
        futures = executor.map(process_region, regions)
        results = list(futures)

    logger.info(f"✅ Execution Complete. Results: {results}")
    return {"statusCode": 200, "body": str(results)}