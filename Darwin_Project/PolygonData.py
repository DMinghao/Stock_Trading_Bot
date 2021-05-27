import csv
import os
import shutil
import random
from collections import defaultdict
from datetime import datetime, timedelta

import pandas as pd
from dotenv import load_dotenv
from polygon import RESTClient
from utility import constant, util
from requests.exceptions import HTTPError
import time

DataDir = './trainingData'
requestCount = 0

def ts_to_datetime(ts):
    return datetime.fromtimestamp(ts / 1000.0).strftime('%Y-%m-%d %H:%M')

def ts_to_date(ts):
    return datetime.fromtimestamp(ts / 1000.0).strftime('%Y-%m-%d')

def ts_to_time(ts):
    return datetime.fromtimestamp(ts / 1000.0).strftime('%H:%M')

def checkCached(stock, date): 
    if not os.path.exists(f'{DataDir}/{stock}'): 
        # pass
        updateAllData(stock)
    if os.path.exists(f'{DataDir}/{stock}/{stock}_{date}.csv'): 
        return True 
    return False 

def writeCSV(stock, date, data): 
    if not os.path.exists(f'{DataDir}/{stock}'):
        os.makedirs(f'{DataDir}/{stock}')
    data_file = open(f'{DataDir}/{stock}/{stock}_{date}.csv', 'w', newline='') 
    csv_writer = csv.writer(data_file) 
    count = 0
    for d in data: 
        if count == 0: 
            header = d.keys() 
            csv_writer.writerow(header) 
            count += 1
        csv_writer.writerow(d.values()) 
    data_file.close() 

def updateAllData(stock): 
    if os.path.exists(f'{DataDir}/{stock}'): 
        return
    fromdate = datetime.today().replace(year=datetime.today().year - 15).strftime("%Y-%m-%d")
    todate = datetime.today().strftime("%Y-%m-%d")
    key = constant.polygon.POLYGON_API_KEY
    # print(key)
    client = RESTClient(key)
    try: 
        resp = client.stocks_equities_aggregates(stock, 1, "minute", fromdate, todate, unadjusted=False)
    except (HTTPError, ConnectionError): 
            print("API call too frequent: thread sleep 1 min")
            time.sleep(60)
            resp = client.stocks_equities_aggregates(stock, 1, "minute", fromdate, todate, unadjusted=False)
    while not hasattr(resp, 'results'): 
        fromdate = datetime.strptime(fromdate, '%Y-%m-%d')
        fromdate += timedelta(days=30)
        fromdate = fromdate.strftime('%Y-%m-%d')
        try: 
            resp = client.stocks_equities_aggregates(stock, 1, "minute", fromdate, todate, unadjusted=False)
        except (HTTPError, ConnectionError): 
            print("API call too frequent: thread sleep 1 min")
            time.sleep(60)
            resp = client.stocks_equities_aggregates(stock, 1, "minute", fromdate, todate, unadjusted=False)
    groups = defaultdict(list)
    for result in resp.results:
        ts = result["t"]
        result["t"] = ts_to_datetime(ts)
        result["date"] = ts_to_date(ts)
        result["time"] = ts_to_time(ts)
        groups[result["date"]].append(result)
    splited = list(groups.values())
    for l in splited: 
        writeCSV(stock, l[0]["date"], l)

def getData(stock, date): 
    if checkCached(stock, date): return f'{DataDir}/{stock}/{stock}_{date}.csv'
    key = constant.polygon.POLYGON_API_KEY
    client = RESTClient(key)
    # if datetime.strptime(date, '%Y-%m-%d') > datetime.now(): 
    try: 
        resp = client.stocks_equities_aggregates(stock, 1, "minute", date, date, unadjusted=False)
    except (HTTPError, ConnectionError): 
            print("API call too frequent: thread sleep 1 min")
            time.sleep(60)
            resp = client.stocks_equities_aggregates(stock, 1, "minute", date, date, unadjusted=False)
    while not hasattr(resp, 'results'): 
        date = datetime.strptime(date, '%Y-%m-%d')
        date += timedelta(days=30)
        date = date.strftime('%Y-%m-%d')
        try: 
            resp = client.stocks_equities_aggregates(stock, 1, "minute", date, date, unadjusted=False)
        except (HTTPError, ConnectionError): 
            print("API call too frequent: thread sleep 1 min")
            time.sleep(60)
            resp = client.stocks_equities_aggregates(stock, 1, "minute", date, date, unadjusted=False)
        # file = ""
        # for root, dirs, files in os.walk(f'{DataDir}/{stock}'):
        #     file = random.choice(files)
        # return f'{DataDir}/{stock}/{file}.csv'
    for result in resp.results:
        ts = result["t"]
        result["t"] = ts_to_datetime(ts)
        result["date"] = ts_to_date(ts)
        result["time"] = ts_to_time(ts)
    writeCSV(stock, date, resp.results)
    return f'{DataDir}/{stock}/{stock}_{date}.csv'

if __name__ == '__main__':
    print(getData('GE', '2000-02-17'))
