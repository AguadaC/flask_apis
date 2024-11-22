# Flask API

This document outlines the necessary steps to run the application and conduct testing.

## Prerequisites

- Create a virtual environment
- Install the required dependencies

## How to Run the Application

- Create a database image using the [following steps](/postgresql/README.md) and run the container.
- Switch to the `testing` branch and within the `app` directory, run the following commands:

```bash
flask db init
flask db migrate
flask db upgrade
```

- Switch back to the `main` branch and run the `run.py` file.

## How to Run Tests

- Switch to the `testing` branch and within the `app` directory, run the following command:

```bash
pytest --cov=app --cov-report html
```

- An `html` directory will be created at the root of the repository containing an `index.html` file where you can view the coverage report.
