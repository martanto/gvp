# config/database.py
# Standard library imports
import os

# Third party imports
from masoniteorm.connections import ConnectionResolver

DATABASES = {
    "default": os.getenv("DB_DEFAULT", "sqlite"),
    "mysql": {
        "host": os.getenv("MYSQL_HOST", "localhost"),
        "driver": "mysql",
        "database": os.getenv("MYSQL_DATABASE", "gvp"),
        "user": os.getenv("MYSQL_USERNAME", ""),
        "password": os.getenv("MYSQL_PASSWORD", ""),
        "port": os.getenv("MYSQL_PORT", 3306),
        "log_queries": False,
        "options": {
            #
        },
    },
    "postgres": {
        "host": os.getenv("POSTGRES_HOST", "localhost"),
        "driver": "postgres",
        "database": os.getenv("POSTGRES_DATABASE", "gvp"),
        "user": os.getenv("POSTGRES_USERNAME", ""),
        "password": os.getenv("POSTGRES_PASSWORD", ""),
        "port": os.getenv("POSTGRES_PORT", 5432),
        "log_queries": False,
        "options": {
            #
        },
    },
    "sqlite": {
        "driver": "sqlite",
        "database": os.getenv("SQLITE_DATABASE", "gvp.db"),
    },
}

DB = ConnectionResolver().set_connection_details(DATABASES)
