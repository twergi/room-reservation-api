# Room Reservation API

## Schema
Available at `/api/`

## Docs
Available at `/api/docs/`

## Instructions
How to run the server:
- install [Docker](https://docs.docker.com/engine/install/);
- create and fill `.env` file (fields are specified in `.env-example`), place it in the same folder as `docker-compose.yaml`;
- `docker compose up` - will start `PostgreSQL` database and `Django` server.

**On the first run you should init the database and superuser**. To do so:
- get the container `id` from `docker`;
- execute `docker exec -it <your_container_id> /source/entrypoint.sh` - this will make migrations and create superuser, if no users exist.