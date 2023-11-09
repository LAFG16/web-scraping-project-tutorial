import pandas as pd
import sqlite3
import matplotlib.pyplot as plt
import requests
import time
from bs4 import BeautifulSoup as bs

#Get into the URL

url = "https://www.macrotrends.net/stocks/charts/TSLA/tesla/revenue"

headers = {'User-agent': 'Mozilla/5.0 (Linux; Android 11; SAMSUNG SM-G973U) AppleWebKit/537.36 (KHTML, like Gecko) SamsungBrowser/14.2 Chrome/87.0.4280.141 Mobile Safari/537.36'}

tesla= requests.get(url, timeout=(5), headers=headers)

#Return the tables

html = tesla.text
soup = bs(html, 'html.parser')
tables = soup.find_all('table')

#Find table Quarterly-Revenue

for table in tables:
    if "Tesla Quarterly Revenue" in table.get_text():
        quarterly_table = table

#Return the data by columns

data = []
for row in quarterly_table.find_all("tr")[1:]:
    cells = row.find_all(["th", "td"])
    date = cells[0].get_text()
    revenue = cells[1].get_text()
    data.append([date, revenue])

#Became into DataFrame

tesla_df = pd.DataFrame(data, columns=["date", "revenue"])

#Cleaning DataFrame

tesla_df = tesla_df.replace("", None)
tesla_df['revenue'] = tesla_df['revenue'].replace("[$,]", "", regex=True)
tesla_df = tesla_df.dropna()

#Became DataFrame into SQL

con = sqlite3.connect("tesla.db")

cur = con.cursor()

tesla_df.to_sql("tesla_data", con= con, if_exists="replace", index=False)

#Convert column Date into a type date

cur.execute("""UPDATE tesla_data SET date = strftime('%Y-%m-%d', date)""")
con.commit()

#Making a Query

cur.execute("""SELECT strftime('%Y', date) AS year, SUM(revenue) as total_revenue from tesla_data GROUP BY year""")
query1 = cur.fetchall()
con.close()

#Converting Query into DataFrame

query = pd.DataFrame(query1, columns = ["year", "revenue"])
print(query)

#1 Vizualization

plt.figure(figsize = (10, 5))
years = query["year"]
revenues = query["revenue"]

plt.plot(years, revenues, label="Revenue")

plt.title("Revenue Evolution")
plt.ylabel("Revenue")
plt.xlabel("Years")
plt.legend()
plt.show()

#2 Vizualization

plt.figure(figsize = (10, 5))
years = query["year"]
revenues = query["revenue"]

plt.bar(years, revenues, label = "Revenue")

plt.title("revenue")
plt.legend()
plt.show()

#3 Vizualization

plt.figure(figsize = (10, 5))
years = query["year"]
revenues = query["revenue"]

plt.scatter(years, revenues, label = "revenues")

plt.title("revenue")
plt.legend()
plt.show()
