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

To run tests, execute a cmd:
```pytest -q```
From the root of the repo.

# TODO
- SQLAlchemy async could be used
- More tests could be written and `coverage` added
- Variables and names could be shorted, but that's a big question - AI agents (if used in the company) will understand the code better with system metaphor naming, long and descriptive.
- Development and production dependencies could be separated in `poetry` index.
- Docker configurations could ignore testing and some other files in production (at my current job, we use 2 different compose files - one for testing, one for production).
- End-to-end tests could be written - considering it's money related functionality it makes sense to run entire user scenarios in testing.
- Again, considering it's money related functionality, makes sense to do formal algorithm verification. There are automated tools, where you describe your algorithm with a logic language, and the system runs all the possible variations to test this algorithm - good for validation and modelling of very edge cases. I myself never used those tools yet, but I build finite state machines or state-transition tables manually in critical cases.

# Commit Messages
For commit messages, I usually follow Conventional Commits standard. Did it here (without scope though, as I did a lot of things at the same time in `accounts` and `transactions`).