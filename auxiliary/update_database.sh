#!/bin/bash

# Akadeemilise aasta alguskuupäev (esmaspäev, DD-MM-YYYY)
start_of_year=30-08-2021
# Virtuaalkeskkonna aktiveerimisfaili absoluutne teekond
env_path=/home/rauno/Documents/Delta/delta_env/bin/activate




SCRIPT=$(readlink -f "$0")
SCRIPTPATH=$(dirname $(dirname "$SCRIPT"))
cd $SCRIPTPATH
export PYTHONPATH=$SCRIPTPATH
source $env_path
echo "Generating the academic calendar..."
python auxiliary/crons/ut_week_generator.py $start_of_year
echo "Parsing employee names..."
python auxiliary/crons/ut_employee_parser.py
echo "Parsing courses (this takes a while)..."
python auxiliary/crons/ut_course_parser.py > /dev/null
echo "Updating course data tables..."
python auxiliary/crons/ut_event_type_updater_en.py
echo "Finished!"
