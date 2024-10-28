# Clinical Trials Pipeline Setup Guide

A pipeline for processing clinical trial data, extracting conditions using LLM, and storing in MongoDB. This was done as an assignment for the academic labs.

## Prerequisites
- Docker and Docker Compose installed
- Git installed
- OpenAI API key

## Clone and Configure
1. Clone the repository:

```bash
git clone <repository-url> taoufik_academic_labs_assignment
cd taoufik_academic_labs_assignment
```
2. Create a `.env` file in the root directory:

```bash
OPENAI_API_KEY=your_openai_api_key_here
```
The already provided key was fully consumed, but the key will nonetheless not error out the job, it wil just write an error in the logs and provide a disease of that same log.


### Key Components
- `clients/`: API and database clients
- `transformations/`: Data transformation strategies
- `pipeline/`: Pipeline orchestration
- `main.py`: Entry point

## Build and Run
1. Build and start the containers:

```bash
docker-compose up --build
```

This will:
- Build the Python application container
- Start MongoDB container
- Link the services together

## Pipeline Execution
The pipeline automatically:
1. Fetches clinical trials data
2. Transforms the data
3. Extracts conditions using OpenAI
4. Stores in MongoDB

## Monitor MongoDB

```bash
docker-compose logs -f app
```

```bash
docker-compose logs -f app
```

## Further improvements
* Add unit tests and integration tests
* Develop CI-CD pipelines : linting, testing, building, deploying
* Add a cron job to run the pipeline every period of time
* Add a way to check if the data is up to date before updating the database, and if it is not up to date, update the database with the new data, this can be done byc hecking the latest update date of the data in the database and comparing it to the latest update date of the data in the mongo db
* Add other datasources (reasearcher, principl investigators, etc...) to enrich the mondodb collection of studies.
* Add other cleaning steps to the pipeline, etc...
* Grafana monitoring of API calls - DB calls.
* Logging/monitoring in the ELK stack.