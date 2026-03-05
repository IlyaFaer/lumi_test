# Structure  
The repository has the following structure:  
- root of the repo contains Docker and Git configurations  
- `app` folder contains the actual web application and all the necessary dependencies  
- `tests` - isolated from the app as on production they are not needed - it'll be easier to separate them e.g. in `.dockerignore`  
  
Inside the `app`:  
- `alembic` - database migrations and migration environment
- `db` - database models and related functions
- `models` - Pydantic data models
- `routers` - endpoints definition
- `services` - business logic
- `dependencies.py` - not used in this project, but makes sense to keep global utilities

There are 2 pieces of functionality: `accounts` and `transactions` (including transaction entries).

# Deployment
Use Docker to deploy the app locally:  
```docker compose up -d```  
On some systems, it may be `docker-compose`.  
  
Migrations are done with `alembic`, the basic migration is already committed into the repo.  
  
For dependencies management, the app uses `poetry`.

# Tests
Tests are ran with `pytest` and consist of 2 parts:
- `unit` - isolated business logic tests
- `integration` - high level tests that use a test database (created and dropped on the tests run)