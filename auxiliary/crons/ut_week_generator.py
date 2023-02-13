# Õppenädalate ning nende algus- ja lõppkuupäevade generaator
# Käsurealt käivitades võib õppeaasta alguskuupäeva anda argumendiga formaadis DD-MM-YYYY (nt. 30-08-2021)
# Tööaeg ATI sülearvutil ~1 minut

import re
import sys
import psycopg2
import datetime

# Kui import ei õnnestu, käivita järgnev käsk:
# export PYTHONPATH="${PYTHONPATH}:/teekond/kausta/Delta_et/"
from auxiliary.database_settings import *

# Õppeaasta alguskuupäev
START_DATE = "29-08-2022"


def generate_weeks(start_date):
    year_start = datetime.datetime.strptime(start_date, "%d-%m-%Y").date()

    conn = psycopg2.connect(host=DATABASE_HOST, port=DATABASE_PORT, database=DATABASE_NAME, user=DATABASE_USER, password=DATABASE_PASSWORD)
    cur = conn.cursor()

    cur.execute("TRUNCATE TABLE ut_weeks;")
    monday = year_start
    for i in range(52):
        cur.execute("INSERT INTO ut_weeks (week_nr, monday, sunday) VALUES ("
                    + str(i+1) + ", '" + str(monday) + "', '" + str(monday + datetime.timedelta(days=6)) + "');")
        monday = monday + datetime.timedelta(days=7)

    cur.close()
    conn.commit()
    conn.close()


if __name__ == '__main__':
    if len(sys.argv) == 1:
        date_string = START_DATE
    else:
        date_string = sys.argv[1]
    if re.fullmatch(r"\d\d-\d\d-\d\d\d\d", date_string) is None:
        raise ValueError('Incorrect date string: expected format is DD-MM-YYYY')
    generate_weeks(date_string)
