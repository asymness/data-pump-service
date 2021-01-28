# Docker Data Pump Service

A data pump service based on Python and Docker that counts the running AWS EC2 instances running across specified regions and sends the data to a webhook via POST request.

### Prerequisites

* Docker

### Configuration

The configration variables are defined in the `env` file in the project root directory. This service supports the following configuration variables:
* `AWS_ACCESS_KEY_ID`: The access key ID of your AWS credentials. (**required**)
* `AWS_SECRET_ACCESS_KEY`: The access key secret of your AWS credentials. (**required**)
* `WEBHOOK_URL`: A URL that supports `POST` request method, to which the polled data should be sent. (**required**)
* `AWS_REGIONS`: A comma-separated list of region names for which to gather the count of running EC2 instances. (**optional**, *default*: All regions)
* `PUMP_INTERVAL`: The interval in minutes after which the service will poll the data source for updated data. (**optional**, *default*: `15`)


### Build

Build the Docker container for this service using
```
docker build -t data-pump-service .
```

### Run

Run the Docker container for this service using
```
docker run -d --env-file=env data-pump-service:latest
```

### Built With

* Python 3.9.1
  * boto3
  * requests


## Authors

* **Asim**
