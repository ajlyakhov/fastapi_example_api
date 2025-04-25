import os
import traceback

import boto3

from app.api.models import TrackingItem
from app.conf.settings import settings
from app.db.base import DatabaseProvider


class DatabaseException(Exception):
    """ Base exception class for all exceptions raised by this module. """
    pass


class DatabaseDynamoDb(DatabaseProvider):
    """ DynamoDB database provider """

    def __init__(self):

        if "STAGE" in os.environ:
            # we don't need to initialize boto parameters for lambda function mode
            # when "STAGE" is inside environment - mean that it is lambda function mode
            dynamo_params = {}
        else:
            dynamo_params = {
                "region_name": settings.AWS_REGION,
                "aws_access_key_id": settings.AWS_ACCESS_KEY_ID,
                "aws_secret_access_key": settings.AWS_SECRET_ACCESS_KEY
            }

        if len(settings.DYNAMODB_ENDPOINT) > 0:
            # only needed for dynamodb local
            dynamo_params['endpoint_url'] = settings.DYNAMODB_ENDPOINT

        self.dynamodb_resource = boto3.resource(
            "dynamodb",
            **dynamo_params,
        )
        self.dynamodb_client = boto3.client(
            "dynamodb",
            **dynamo_params,
        )
        self.shipments_table = self.dynamodb_resource.Table(settings.TRACKING_TABLE)

    def get_tracking_item(self, tracking_number: str, carrier: str) -> TrackingItem | None:
        """Search for tracking item by tracking number and carrier

        :param tracking_number: requested tracking number
        :param carrier: requested carrier
        :return: TrackingItem or None
        """

        try:
            response = self.shipments_table.query(
                KeyConditionExpression="tracking_number = :tn AND carrier = :c",
                ExpressionAttributeValues={
                    ":tn": tracking_number,
                    ":c": carrier
                }
            )
            if response["Count"] > 0:
                return TrackingItem(**response["Items"][0])
            else:
                return None
        except Exception as e:
            raise DatabaseException(f"DynamoDB database not initialized: {e}, trace: {traceback.format_exc()}")

    def put_tracking_items(self, items: list) -> None:
        """Bulk method to put tracking items into DynamoDB

        :param items: list of tracking items
        :return: None
        """
        with self.shipments_table.batch_writer() as batch:
            for item in items:
                batch.put_item(Item=item)

    def create_tracking_table(self) -> None:
        """Automatically generate DynamoDB Tracking table, if exists - delete it and create again.
        Only used for demo purposes.
        """
        existing_tables = self.dynamodb_client.list_tables()['TableNames']
        print(f"Existing tables: {existing_tables}")
        if self.shipments_table.name in existing_tables:
            self.shipments_table.delete()

        table = self.dynamodb_resource.create_table(
            TableName=self.shipments_table.name,
            KeySchema=[
                {'AttributeName': 'tracking_number', 'KeyType': 'HASH'},  # Partition key
                {'AttributeName': 'carrier', 'KeyType': 'RANGE'}  # Sort key
            ],
            AttributeDefinitions=[
                {'AttributeName': 'tracking_number', 'AttributeType': 'S'},  # String
                {'AttributeName': 'carrier', 'AttributeType': 'S'}  # String
            ],
            ProvisionedThroughput={'ReadCapacityUnits': 1, 'WriteCapacityUnits': 1}
        )

        # Wait until table is created
        table.wait_until_exists()

        print(f"Table '{self.shipments_table.name}' created successfully!")
