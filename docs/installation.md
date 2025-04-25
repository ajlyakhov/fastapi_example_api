# Folder Structure

- **app** – FastAPI application.
- **data** – Contains CSV files for database initialization.
- **deploy** – Deployment configuration files.
- **docs** – Project documentation.
- **test** – Unit & integration tests.


- **.env.dev** - environment file for app debugging mode
- **.env.lambda** - environment for AWS Lambda mode
- **.env.local** - environment for inside docker mode
- **.env.test** - environment for unit tests


- **serverless.yml** - serverless configuration
- **requirements.txt** - dependencies, installed by pip


- **pytest.ini** - pytest unittests configuration


- **readme.md** - documentation index

# Installation Steps

## Option 1: Local Docker (One-Command Startup)

Run the following command to start the service using Docker:

```sh
cd folder_with_trackapi

docker-compose -f deploy/docker/docker-compose.yml up
```

This command will start three Docker containers: 
- trackapi (FastAPI application)
- DynamoDB (with initial data population) 
- Redis (for caching)

Data will be automatically loaded into DynamoDB (using forth temporary container).

Upon restarting the project, shipment data will be reinitialized. 
While data persistence across restarts is possible, it is not enabled for demo purposes.

## Option 2. Local development environment

You need to start redis and dynamodb_local locally, for example using docker:

```
cd folder_with_trackapi

docker-compose -f deploy/docker/docker-compose.local.yml up -d
```

Configure virtual environment, install dependencies and run the dev server:

```
python3 -m venv venv
source venv/bin/activate

pip install -r requirements.txt

ENV=dev uvicorn app.main:app --reload
```


## Option 3. AWS serverless setup

Set up the Serverless deployment. Ensure you have a registered Serverless account and an AWS account.

Additionally, AWS CLI access must be properly configured (aws configure completed).

This setup assumes the use of Serverless v4.

```
npm install -g serverless
npm install --save-dev serverless-dotenv-plugin
npm install --save-dev serverless-python-requirements
```

Login into serverless with your credentials:

```
serverless login
```

Define AWS profile (in case of many), here:

~/.aws/config

For example:

```
[profile trackapi]
aws_access_key_id = xxxxx                                                                                                                     
aws_secret_access_key = xxxxx

[default]
region = eu-central-1
```

Export variable in env to force specific AWS profile usage:

```
export AWS_PROFILE=trackapi
```

### Deploy:

```
serverless deploy
```

### Remove deployment:

```
serverless remove
```
