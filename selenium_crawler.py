from selenium import webdriver
from bs4 import BeautifulSoup
import time
import sqlite3
import random

#setting up a database
conn = sqlite3.connect('dou.db')
cur = conn.cursor()

cur.executescript('''
	DROP TABLE IF EXISTS Companies;
	DROP TABLE IF EXISTS Offices;
	DROP TABLE IF EXISTS Vacancies;

	CREATE TABLE Companies (
	id INTEGER NOT NULL PRIMARY KEY AUTOINCREMENT UNIQUE,
	name TEXT UNIQUE,
	link TEXT UNIQUE
	);

	CREATE TABLE Offices (
	id INTEGER NOT NULL PRIMARY KEY AUTOINCREMENT UNIQUE,
	company_id INTEGER,
	city TEXT,
	address TEXT
	);

	CREATE TABLE Vacancies (
	company_id INTEGER,
	office_id INTEGER,
	link TEXT
	);
	''')
#set up user-agent and get page
browser = webdriver.Firefox()
url = 'https://jobs.dou.ua/companies/'
browser.get(url)


#inside while loop triggering ajax on the page to load all elements at once
while browser.find_elements_by_xpath('//*[@id="companiesListId"]/div/a'):
	try:
		browser.find_elements_by_xpath('//*[@id="companiesListId"]/div/a')[0].click()
		#here and on using time and random modules to wait before repeting request
		wait = random.random()
		time.sleep(wait)
	except:
		break

#parsing the page with BS, getting all companies objects
soup = BeautifulSoup(browser.page_source, 'html.parser')
companies = soup.select('.l-items .company')
#get name and link for every company 
for company in companies:
	name = company.select('.cn-a')[0].text
	link = company.select('.cn-a')[0].get('href')
	cur.execute("INSERT OR IGNORE INTO Companies (name, link) VALUES (?, ?)", (name, link))
	cur.execute("SELECT id FROM Companies WHERE name = ?", (name, ))
	company_id = cur.fetchone()[0]

	#using company link to build link to offices page and repeat previous steps
	office_url = link + "offices"
	browser.get(office_url)
	office_soup = BeautifulSoup(browser.page_source, 'html.parser')
	offices = office_soup.select('.city')

	#for every office get city, and address
	for office in offices:
		try:
			city = office.select('h4')[0].text
			address = office.select('.address')[0].text.strip()
			address = address[0: address.find('(')]

			cur.execute("INSERT OR IGNORE INTO Offices (company_id, city, address) VALUES (?, ?, ?)", (company_id, city, address))
			cur.execute("SELECT id FROM Offices WHERE city = ?", (city, ))
			office_id = cur.fetchone()[0]

		except:
			pass

		print("City: {}\nAddress: {}".format(city, address))

	print("Name: {}\nLink: {}".format(name, link))
	#commit changes to database
	conn.commit()
	wait = random.random() * 5
	time.sleep(wait)
browser.quit()