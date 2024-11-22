# Data Base Structure.

## Commands to build and run

- Build

```bash
docker build -t movies-postgres-image .
```

- Run

```bash
docker run --name movies-postgres-container -p 5432:5432 -d movies-postgres-image
```

- Enter to the container

```bash
docker exec -it movies-postgres-container psql -U postgres
```

- List data_bases: `\l`
- Change data_base: `\c data_base_name`
- List tables: `\dt`
