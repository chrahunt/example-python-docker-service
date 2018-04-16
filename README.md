# example-python-docker-service

Example of running a simple Python script in Docker.

```sh
docker-compose up
# when changes have been made
docker-compose build && docker-compose up
```

## development

Models for resolving development issues when working on Python docker
services.

### if package is external to Dockerfile repository

Copy package into directory before doing Docker build, or provide a git URL
to the `context` key in the `docker-compose.yml`.

### if locally-developed packages are used

When doing development on a Dockerized Python application, locally
developed packages also need to be available to the app.

Run a local [`pypiserver`](https://pypi.python.org/pypi/pypiserver)
and symlink all locally-developed packages into the packages directory.
Expose the URL using `PIP_EXTRA_INDEX_URL` at build-time (by editing the
`Dockerfile`) or at runtime by running an entrypoint script. To always
pick up new changes run `docker-compose build --no-cache`.

## production

### notification

Provide authorization credentials via Docker secrets to the application,
reading the location from environment variables.

### logging

Use built-in Docker logging drivers to direct container stderr logs to the
desired location.