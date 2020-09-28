#!/usr/bin/python
import json
from datetime import timedelta
import sys
import pandas as pd
import requests
import configparser
import os

""" 
Command to execute: 

python3 keka_timesheet_filling.py <first_arg> <second_arg> <third_arg> <fourth_arg>

first_arg: path to the csv file
second_arg: start_date
third_arg: end_date
fourth_arg: cookie
"""

# Config parser
config = configparser.ConfigParser()
config.read(os.path.join(os.getcwd(), 'config.ini'))

filepath = config.get("FILE_DETAILS", "PATH")
start_date = config.get("DETAILS", "START_DATE")
end_date = config.get("DETAILS", "END_DATE")
billing_id = config.get("PROJECT_DETAILS", "BILLING_ID")
task_id = config.get("PROJECT_DETAILS", "TASK_ID")
project_id = config.get("PROJECT_DETAILS", "PROJECT_ID")
cookie = config.get("DETAILS", "COOKIE")

df = pd.read_csv(str(filepath))
df['Date'] = pd.to_datetime(df['Date'])
new_df = df[df["Date"].between(start_date, end_date)]
headers = {
    "accept": "application/json, text/plain, */*",
    "accept-encoding": "gzip, deflate, br",
    "accept-language": "en-GB,en-US;q=0.9,en;q=0.8",
    "content-type": "application/json;charset=UTF-8",
    "cookie": cookie,
    "dnt": "1",
    "origin": "https://knoldus.keka.com",
    "referer": "https://knoldus.keka.com/",
    "user-agent": "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/74.0.3729.108 Safari/537.36",
    "x-requested-with": "XMLHttpRequest"
}

for index, row in new_df.iterrows():
    previous_date = (row["Date"] - timedelta(1)).strftime('%Y-%m-%dT18:30:00.000Z')
    current_date = str(row['Date'].to_pydatetime().date())
    if pd.notna(row["Description"]):
        url = 'https://knoldus.keka.com/api/mytime/timesheet'
        data = json.dumps({"timesheet": {"startDate": str(previous_date), "endDate": str(current_date)},
                           "timesheetEntries": [
                               {"date": str(current_date), "projectId": project_id,
                                "taskId": task_id, "startTime": "10:45",
                                "endTime": "18:45", "totalHours": 9,
                                "comments": str(row.Description), "billable": "true",
                                "billingClassificationId": billing_id, "sequenceNumber": 1}]})
        res = requests.post(url=url, data=data, headers=headers)
        print("-------------------------------------------")
        if res.status_code == 200:
            print("Successful for date: " + str(current_date))
        else:
            print("Unsuccessful for date: " + str(current_date))
    else:
        print("*****************************************")
        print("Skipping for date: " + str(current_date))
