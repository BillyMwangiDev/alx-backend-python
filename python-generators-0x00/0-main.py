#!/usr/bin/python3

import logging

import seed

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s %(levelname)s %(name)s %(message)s",
)

connection = seed.connect_db()
seed.create_database(connection)
seed.create_table(connection)
seed.insert_data(connection, "user_data.csv")

cursor = connection.cursor()
cursor.execute("SELECT COUNT(*) FROM user_data;")
count = cursor.fetchone()[0]
print(f"Database ready. {count} users loaded.")
cursor.close()
connection.close()
