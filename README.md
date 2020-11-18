## Discord bot template

Starting point for a python discord bot

---

> This assumes you already have a MariaDB instance set up and running

Get the source code and setup python environment using pipenv:
```
$ git clone https://joinemm/discord-bot-template
$ cd discord-bot-template
$ pipenv install
```

Fill out the `config.toml.example` with your own values and rename it to `config.toml`.

Build the database schema:
```
[]> CREATE DATABASE dbname;
$ mysql dbname < sql/schema.sql
```

If everything went well you should be able to run the bot with

```
$ pipenv run python main.py
```