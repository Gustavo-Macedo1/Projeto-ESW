import mysql.connector
from mysql.connector.pooling import MySQLConnectionPool


DB_CONFIG = {
    "user": "root",
    "password": "pass123",
    "port": "3306",
    "host": "127.0.0.4",
    "database": "banco",
}

_connection_pool = MySQLConnectionPool(pool_name="seeban_pool", pool_size=5, **DB_CONFIG)


def get_connection():
    return _connection_pool.get_connection()
