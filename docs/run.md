# Running demo

Assuming you run a local installation, then follow this steps:

1. Start trackapi

```
docker compose -f deploy/docker/docker-compose.yml up
```

2. Open in your browser:

http://localhost:8000/docs

2. On this swagger documentation page press "Try it out" and the "Execute". 
For you convenience, example request already preconfigured.

3. This request should return 200 OK with JSON data as a response to your request.

For example:

```
{
  "tracking": {
    "tracking_number": "TN12345678",
    "carrier": "DHL",
    "sender_address": "Street 1, 10115 Berlin, Germany",
    "receiver_address": "Street 10, 75001 Paris, France",
    "status": "in-transit",
    "articles": [
      {
        "article_name": "Laptop",
        "article_quantity": 1,
        "article_price": 800,
        "SKU": "LP123"
      },
      {
        "article_name": "Mouse",
        "article_quantity": 1,
        "article_price": 25,
        "SKU": "MO456"
      }
    ]
  },
  "weather": {
    "wind": "south-southeast",
    "temp": 13.9,
    "city": "Paris",
    "cloud": 64,
    "description": "Scattered clouds"
  }
}
```

