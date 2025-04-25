import csv

from app.db.dynamodb import DatabaseDynamoDb
from app.conf.settings import settings


def load_shipments_from_csv(csv_filename):
    """Load shipments from csv file

    :param csv_filename: csv file path with shipments
    """

    database = DatabaseDynamoDb()
    database.create_tracking_table()
    with open(csv_filename, newline="", encoding="utf-8") as csvfile:
        reader = csv.DictReader(csvfile)
        items = {}
        for row in reader:
            key = (row["tracking_number"], row["carrier"])
            if key not in items:
                items[key] = {
                    "tracking_number": row['tracking_number'],
                    "carrier": row['carrier'],
                    "sender_address": row['sender_address'],
                    "receiver_address": row['receiver_address'],
                    "status": row['status'],
                    "articles": [{
                        "article_name": row['article_name'],
                        "article_quantity": row['article_quantity'],
                        "article_price": row['article_price'],
                        "SKU": row['SKU']
                    }]
                }
            else:
                items[key]["articles"].append({
                    "article_name": row['article_name'],
                    "article_quantity": row['article_quantity'],
                    "article_price": row['article_price'],
                    "SKU": row['SKU']
                })
        database.put_tracking_items([value for key, value in items.items()])
        print('Items uploaded in table')


if __name__ == "__main__":
    load_shipments_from_csv("/app/data/shipments.csv")
