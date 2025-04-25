# API Architecture

## Key Considerations in API Design

1. The core business logic of the API is straightforward, primarily consisting of a single endpoint that retrieves data from the database.
2. The API must efficiently handle high-load environments (1000+ RPS).
3. Request execution time should be minimal—measured in tens of milliseconds.


### Production Deployment Considerations

In a production environment, the API must support 1000+ RPS and be deployed in the cloud (AWS, for simplicity). The key infrastructure requirements are:

1. Scalability to handle high request rates.
2. Caching to reduce external weather API requests.
3. A database optimized for fast retrieval of shipment data.
4. A document-based data structure, eliminating the need for a relational database.

#### Infrastructure:

- **AWS Lambda + API Gateway** – Provides auto-scaling and granular request control.
- **DynamoDB** – A NoSQL database capable of handling high RPS.
- **ElastiCache** – Caches weather data with a 2-hour expiration.
- **Serverless Framework** – Manages deployment efficiently.

### Benefits:

- The entire infrastructure is managed via a single `serverless.yml` file.
- AWS Lambda ensures automatic scalability, adapting to any load.
- Costs are directly tied to actual API usage, optimizing expenses.

### Note:

- For APIs with constant highload preferable alternative would be Fargate or simple EC2 implementation, to get rid of periodic lambda initialization time
