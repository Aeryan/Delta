import psycopg2
import datetime

START_OF_YEAR = datetime.date(2020, 8, 31)

conn = psycopg2.connect(host="localhost", port=5432, database="delta", user="postgres", password="postgres")
cur = conn.cursor()

cur.execute("TRUNCATE TABLE ut_weeks;")
monday = START_OF_YEAR
for i in range(52):
    cur.execute("INSERT INTO ut_weeks (week_nr, monday, sunday) VALUES ("
                + str(i+1) + ", '" + str(monday) + "', '" + str(monday + datetime.timedelta(days=6)) + "');")
    monday = monday + datetime.timedelta(days=7)

cur.close()
conn.commit()
conn.close()
