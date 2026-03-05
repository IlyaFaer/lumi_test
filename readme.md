# Structure  
Root of the repo contains Docker and Git configurations.  
`app` folder contains the actual web application. Inside it, the structure is the following:  
`db` - database models and related functions  
`models` - Pydantic data models  
`routers` - endpoints  
`services` - business logic  
`tests` - testing utilities  

There are 2 pieces of functionality: `accounts` and `transactions` (including transaction entries).

# Deployment
Use Docker to deploy the app locally:  
```docker compose up -d```  
On some systems, it may be `docker-compose`.

# Dependencies
For dependencies management, the app uses `poetry`.