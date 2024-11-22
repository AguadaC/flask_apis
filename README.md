# Flask API

This document outlines the necessary steps to run the application and conduct testing.

## Prerequisites

- Create a virtual environment
- Install the required dependencies

## How to Run the Application

> [!IMPORTANT]
> Always start with a new database!

- Create a database image using the [following steps](/postgresql/README.md) and run the container.
- Switch to the `testing` branch and within the `app` directory, run the following commands:

```bash
flask db init
flask db migrate
flask db upgrade
```

- Switch back to the `main` branch and run the `run.py` file.
- [HERE](postman_collection.json) you have a Postman Collection to use the app.

## How to Run Tests

- Switch to the `testing` branch and within the `app` directory, run the following command:

```bash
pytest --cov=app --cov-report html
```

- An `html` directory will be created at the root of the repository containing an `index.html` file where you can view the coverage report.

## Considerations and Improvements

### Considerations

- I decided to use a PostgreSQL database to test the modularity of the code. The app works with this database, and the tests are executed with a volatile database. This approach covers both possibilities offered.
- The focus is on testing and the resilience of the API.An 85% test coverage was achieved.
- To simplify:
    - Favorite movies are not sorted.
    - Options were hardcoded (for example, User_ID).
    - Instead of a Redis database, a singleton class was used as a cache.
    - The exposed API routes are not protected.

### Improvements

- Proper modularization of the database, with the corresponding tables.
- Implementation of Redis.
- Implementation of authentication and authorization.
- Management of environment variables for greater flexibility in configuration.
- Remove hardcoded values and add management for these variables.
