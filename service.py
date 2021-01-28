import logging
import time
import os
import sys
import uuid

import requests
from boto3.session import Session
import botocore


logging.basicConfig(
    level=logging.INFO,
    format="{asctime} {levelname:<8} {message}",
    style="{"
)


def get_running_instances(regions):
    session = Session()

    # Get available regions for EC2
    ec2_regions = session.get_available_regions('ec2')

    # Get regions defined in evironment variables
    if regions:
        config_regions = [region.strip() for region in regions.lower().split(",")]
    else:
        config_regions = ec2_regions
    logging.info(f"Gathering running EC2 instances count for the following regions: {', '.join(config_regions)}")

    # create filter for instances in running state
    filters = [
        {
            'Name': 'instance-state-name', 
            'Values': ['running']
        }
    ]

    regionwise_data = []
    total_instances = 0

    for region in config_regions:
        if region not in ec2_regions:
            logging.critical(
                f"The region '{region}' is not a valid region for EC2. "
                "Please check AWS_REGIONS environment variable. Continuing..."
            )
            continue
        logging.debug(f"Getting EC2 instances for {region}")
        ec2_conn = session.resource("ec2", region_name=region)
        try:
            instance_count = len(list(ec2_conn.instances.filter(Filters=filters)))
        except botocore.exceptions.ClientError as error:
            logging.critical(
                f"Unable to get instances for region {region} using the provided credentials.", 
                exc_info=error
            )
            continue
        logging.debug(f"Found {instance_count} running EC2 instances in {region}.")
        total_instances += instance_count
        regionwise_data.append({
            "region": region,
            "count": instance_count
        })
    logging.info(f"Found {total_instances} running EC2 instances across specified regions.")
    return total_instances, regionwise_data


def post_to_webhook(url, total_count, regionwise_data):
    headers = {'x-editor-id': str(uuid.uuid4())}
    post_data = {
        'entity_id': 'ec2_running_instances',
        'properties': [{'current_value': total_count}, {'regionwise_data': regionwise_data}]
    }
    response = requests.post(url, json=post_data, headers=headers)
    if not response.ok:
        logging.critical(f"Encountered status code {response.status_code} while posting data to {url}.")
    logging.info("Posted data to webhook URL successfully.")
    logging.info("Pump successful.")


if __name__ == "__main__":
    # Verify and get environment variables.
    webhook_url = os.getenv("WEBHOOK_URL")
    if not webhook_url:
        logging.critical("WEBHOOK_URL environment variable is not set.")
        sys.exit(1)
    if Session().get_credentials() is None:
        logging.critical(
            "Please provide AWS credentials via the AWS_ACCESS_KEY_ID "
            "and AWS_SECRET_ACCESS_KEY environment variables."
        )
        sys.exit(1)
    regions = os.getenv("AWS_REGIONS")
    pump_interval = int(os.getenv("PUMP_INTERVAL", 15))

    # Start data pump service
    logging.info("** Started data pump service for EC2 instances **")
    while True:
        logging.info("Pump started...")
        instance_count, regionwise_data = get_running_instances(regions)
        post_to_webhook(webhook_url, instance_count, regionwise_data)
        logging.info(f"Sleeping for {pump_interval} minute(s)...")
        time.sleep(pump_interval * 60)
