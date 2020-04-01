#Scrape county level data from https://www.indexmundi.com/facts/united-states/quick-facts
import requests
import pandas as pd
from selenium import webdriver
from bs4 import BeautifulSoup
import time
import os.path
import pickle

data_dict = {
"State": "",
"County": "",
"Population estimates, July 1, 2019,  (V2019)": "",
"Population, percent change - April 1, 2010 (estimates base) to July 1, 2019,  (V2019)": "",
"Population estimates base, April 1, 2010,  (V2019)": "",
"Population, Census, April 1, 2010": "",
"Persons under 5 years, percent": "",
"Persons under 18 years, percent": "",
"Persons 65 years and over, percent": "",
"Female persons, percent": "",
"White alone, percent": "",
"Black or African American alone, percent": "",
"American Indian and Alaska Native alone, percent": "",
"Asian alone, percent": "",
"Native Hawaiian and Other Pacific Islander alone, percent": "",
"Two or More Races, percent": "",
"Hispanic or Latino, percent": "",
"White alone, not Hispanic or Latino, percent": "",
"Veterans, 2014-2018": "",
"Foreign born persons, percent, 2014-2018": "",
"Housing units,  July 1, 2018,  (V2018)": "",
"Owner-occupied housing unit rate, 2014-2018": "",
"Median value of owner-occupied housing units, 2014-2018": "",
"Median selected monthly owner costs -with a mortgage, 2014-2018": "",
"Median selected monthly owner costs -without a mortgage, 2014-2018": "",
"Median gross rent, 2014-2018": "",
"Housing units in multi-unit structures, percent, 2009-2013": "",
"Building permits, 2018": "",
"Households, 2014-2018": "",
"Persons per household, 2014-2018": "",
"Living in same house 1 year ago, percent of persons age 1 year+, 2014-2018": "",
"Language other than English spoken at home, percent of persons age 5 years+, 2014-2018": "",
"Households with a computer, percent, 2014-2018": "",
"Households with a broadband Internet subscription, percent, 2014-2018": "",
"High school graduate or higher, percent of persons age 25 years+, 2014-2018": "",
"Bachelor's degree or higher, percent of persons age 25 years+, 2014-2018": "",
"With a disability, under age 65 years, percent, 2014-2018": "",
"Persons  without health insurance, under age 65 years, percent": "",
"In civilian labor force, total, percent of population age 16 years+, 2014-2018": "",
"In civilian labor force, female, percent of population age 16 years+, 2014-2018": "",
"Total accommodation and food services sales, 2012 ($1,000)": "",
"Total health care and social assistance receipts/revenue, 2012 ($1,000)": "",
"Total manufacturers shipments, 2012 ($1,000)": "",
"Total merchant wholesaler sales, 2012 ($1,000)": "",
"Total retail sales, 2012 ($1,000)": "",
"Total retail sales per capita, 2012": "",
"Mean travel time to work (minutes), workers age 16 years+, 2014-2018": "",
"Median household income (in 2018 dollars), 2014-2018": "",
"Per capita income in past 12 months (in 2018 dollars), 2014-2018": "",
"Persons in poverty, percent": "",
"Total employer establishments, 2017": "",
"Total employment, 2017": "",
"Total annual payroll, 2017 ($1,000)": "",
"Total employment, percent change, 2016-2017": "",
"Total nonemployer establishments, 2017": "",
"All firms, 2012": "",
"Men-owned firms, 2012": "",
"Women-owned firms, 2012": "",
"Minority-owned firms, 2012": "",
"Nonminority-owned firms, 2012": "",
"Veteran-owned firms, 2012": "",
"Nonveteran-owned firms, 2012": "",
"Black-owned firms, percent, 2007": "",
"American Indian- and Alaska Native-owned firms, percent, 2007": "",
"Asian-owned firms, percent, 2007": "",
"Native Hawaiian- and Other Pacific Islander-owned firms, percent, 2007": "",
"Hispanic-owned firms, percent, 2007": "",
"Women-owned firms, percent, 2007": "",
"Population per square mile, 2010": "",
"Land area in square miles, 2010": ""
}

if(os.path.exists('./state_link_dict.p')):
    print("loading link list")
    state_dict = pickle.load( open( "state_link_dict.p", "rb" ) )

#### Preprocessing, getting list of links ####
else:
    print("could not find link list, creating one now")
    driver = webdriver.Firefox()
    URL = 'https://www.indexmundi.com/facts/united-states/quick-facts'
    driver.get(URL)
    state_dict = {}
    state_link_list = []
    UL_XPATH = '/html/body/div[1]/div[2]/div[2]/div[2]/div[1]/ul'

    state_list = driver.find_element_by_xpath(UL_XPATH)
    states = state_list.find_elements_by_tag_name('li')
    #for each state, get link
    for s in states:
        state_link_list.append(s.find_element_by_tag_name('a').get_attribute("href"))
        print(s.find_element_by_tag_name('a').get_attribute("href"))

    #for each state, get list of counties' links
    for state_url in state_link_list:
        county_link_list = []
        driver.get(state_url)
        county_list = driver.find_element_by_xpath(UL_XPATH)
        counties = county_list.find_elements_by_tag_name('li')
        for c in counties:
            county_link_list.append(c.find_element_by_tag_name('a').get_attribute("href"))
        #dictionary stores list of county links
        state_dict[state_url] = county_link_list
    driver.close()
    pickle.dump(state_dict, open( "state_link_dict.p", "wb" ) )

#If scraping has not already occurred
if(not os.path.exists('./county_data_dict_list.p')):
    #data list is list of individual county dictionaries
    data_list = []
    #For each state, scrape its county level data
    for state in state_dict:
        state_clean = state.split('/')[-1].upper()
        print(state_clean)
        counties = state_dict[state]
        #for each county in the state
        for county_url in counties:
            #Create new county dictionary
            current_county_dict = data_dict.copy()
            current_county_dict['State'] = state_clean
            #go to site and scrape
            website_url = requests.get(county_url).text
            soup = BeautifulSoup(website_url,'html.parser')
            county_name = soup.find('h1').get_text()[:-6].upper()
            current_county_dict['County'] = county_name
            table = soup.find('table')
            #process each row in table
            rows = table.findAll('tr')
            for row in rows:
                cols = row.findAll('td')
                #if one col then just a header
                #if three cols, take last two cols
                if(len(cols)==3):
                    x = cols[1].get_text()
                    y = cols[2].get_text()
                    current_county_dict[x] = y
            data_list.append(current_county_dict)
    pickle.dump(data_list, open( "county_data_dict_list.p", "wb" ) )
else:
    data_list = pickle.load( open( "county_data_dict_list.p", "rb" ) )

df = pd.DataFrame(data_list)
df.to_csv('scrape_demographics.csv')

