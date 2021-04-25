# Docker Flask Example

Demo flask application connected to mongodb with kubernetes compliant health probe endpoints.

```yml
version: "3.9"

volumes: 
  mongodb_data:

services:
  flask:
    build: ./
    ports: [5000:5000]
    volumes: ["./logs:/logs"]
    environment: 
      MONGO_DSN: mongodb://root:rootpassword@mongodb/   # valid rfc connection string
      GUNICORN_CMD_ARGS: "--capture-output"             # see docs for all options
      LOG_LEVEL: error                                  # debug|info|warning|error|critical
      LOG_FORMAT: json                                  # json|text
      FILTER_PROBES: '1'                                # 0|1 - dont log requests to healthcheck endpoints with access logger

  mongodb:
    image: mongo:latest
    environment:
      MONGO_INITDB_ROOT_USERNAME: root
      MONGO_INITDB_ROOT_PASSWORD: rootpassword
    volumes:
      - mongodb_data:/data/db

```

## Start the app

The below command will start the flak application and a mongodb in docker container.

```console
docker-compose up
```

Once the container are running, the flask documentation can be downloaded as pdf

```console
curl localhost:5000/pdf > flask.pdf
```

There is also an endpoint to accept message posts.

```console
$ curl -i -H "Content-Type: application/json" -X POST -d '{"message":"hello, flask"}' http://localhost:5000/msg
HTTP/1.1 201 CREATED
Server: gunicorn
Date: Sat, 24 Apr 2021 15:08:22 GMT
Connection: keep-alive
Content-Type: application/json
Content-Length: 34

{"id":"60843466092d7c719ec5063b"}
```

A list of all messages can be retrieved on the root endpoint.

```console
$ curl localhost:5000/
[{"_id": {"$oid": "60843466092d7c719ec5063b"}, "message": "hello, flask"}]
```

## Health Probe

As long as the app is running it will serve a 200 response on the `/alive` endpoint.

```console
$ curl -I localhost:5000/alive
HTTP/1.0 200 OK
Content-Type: application/json
Content-Length: 24
Server: Werkzeug/1.0.1 Python/3.9.4
Date: Fri, 23 Apr 2021 14:34:54 GMT
```

As long as the database connection is working the app will return a 200 response on `/ready`.

```console
$ curl -Is localhost:5000/ready | head -n 1
HTTP/1.0 200 OK
```

The behavior can be be tested by shutting down the database container. Once the database is down, the application with return a status 503 response.

```console
$ docker-compose stop mongodb
$ curl -Is localhost:5000/ready | head -n 1
HTTP/1.0 503 SERVICE UNAVAILABLE
```

Once the database is started up again the app will return again a 200.

```console
$ docker-compose start mongodb
$ curl -Is localhost:5000/ready | head -n 1
HTTP/1.0 200 OK
```

## Environment

### Logging

The format of the output is by default `json` to play nicely with modern tools. However it can be set to `text` via the enironment variabe `LOG_FORMAT`. Likewise the log level can be set via `LOG_LEVEL`.

```yml
LOG_LEVEL: info     # debug|info|warning|error|critical
LOG_FORMAT: json    # json|text
```

The application logs by default into to stdout and stderr. The output can also be directed to log files if needed. For this the gunicons command line args or flags can be used.

```yml
volumes: ["./logs/logs"]
environment: ["GUNICORN_CMD_ARGS=--capture-output"]
```

### Database DSN

The connection string is set via

```yml
MONGO_DSN: mongodb://user:password@server/
```

### Gunicorn

The `GUNICORN_CMD_ARGS` variable can be used as per [documentation](https://docs.gunicorn.org/en/20.1.0/configure.html). This can be useful do do some tweaking ad hoc.

```yml
GUNICORN_CMD_ARGS: "--workers=6 --threads=4"
```

## Development

The project is using pipenv to manage dependencies. It can be useful to set up the virtual environment locally.

```console
pipenv shell
pipenv sync -d
```

Install the `pre-commit hook`

```console
pre-commit install
```

Flake8 has been configured to accept a maximum line length of 119. When using VS Code, the following settings can be used in order to have alignment with the pre commit hook.

```json
{
    "python.linting.enabled": true,
    "python.linting.pylintEnabled": false,
    "python.linting.flake8Enabled": true,
    "python.formatting.provider": "black"
}
```

## Testing

For testing a compose file exists at the root directory. It will build the image with an exta argument to install the dev dependencies. Addtionally the configuration in this file silence the mongodb output so that the `pytest` output can be viewed.

The following command will start the app and a test database container and run the test suit.

```console
docker-compose -f test-compose.yml up --build && docker-compose -f test-compose.yml down
```

## Makefile

For convenience both the regular start and the test start command have beed placed in a Makefile.

```console
make
make test
```
