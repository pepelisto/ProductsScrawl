import pandas as pd
import sqlite3
import sqlalchemy

con = sqlite3.connect('db.sqlite')

c = con.cursor()

# c.execute("SELECT * FROM products WHERE name='Orange, Seedless'")
c.execute("SELECT * FROM products")# WHERE branch='RHSM'")
print(c.fetchall())

con.commit()

con.close()