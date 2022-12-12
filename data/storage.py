import sqlite3

conn = sqlite3.connect("/root/db/food_adviser_data.db", check_same_thread=False)
cursor = conn.cursor()
