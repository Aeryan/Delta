# Õppenädalate ning nende algus- ja lõppkuupäevade generaator
# Tööaeg ATI sülearvutil ~1 minut

import psycopg2
import datetime

# Andmebaasi seaded
DATABASE_HOST = "localhost"
DATABASE_PORT = 5432
DATABASE_NAME = "delta"
DATABASE_USER = "postgres"
DATABASE_PASSWORD = "postgres"

# Õppeaasta alguskuupäev, siin 31. august 2020
START_OF_YEAR = datetime.date(2020, 8, 31)

conn = psycopg2.connect(host=DATABASE_HOST, port=DATABASE_PORT, database=DATABASE_NAME, user=DATABASE_USER, password=DATABASE_PASSWORD)
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
