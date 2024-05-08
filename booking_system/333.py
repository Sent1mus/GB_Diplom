import sqlite3

# Connect to the SQLite database
conn = sqlite3.connect('db.sqlite3')
cursor = conn.cursor()

# Query to select all records from the auth_user table
query = "SELECT * FROM booking_customer"
cursor.execute(query)

# Fetch all rows from the query
rows = cursor.fetchall()

# Print each row
for row in rows:
    print(row)

# Close the connection
conn.close()
