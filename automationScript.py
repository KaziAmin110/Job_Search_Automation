#Name : Kazi Amin
#Project : Automation of Job Searching Process using Python
#Description : Automation of Job Search Task by Copying information regarding available job listings on various websites and copying important descriptions and links to a Google Sheets document using Sheets API
#Currently supports listings from indeed.com

#Imports
import gspread, time
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.support.wait import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.action_chains import ActionChains
from selenium.common.exceptions import NoSuchElementException


#Google Sheets authentication / Path to Sheets JSON File
gc = gspread.service_account(filename='C:\\Users\\Seam\\OneDrive\\Desktop\\Automate the Boring Stuff Course\\Sheet Credential JSON File\\credentials.json') 

#Driver Options
options = webdriver.ChromeOptions()

options.add_experimental_option("detach", True)

options.add_argument('--window-size=1920,1080')
options.add_argument('--no-sandbox')
options.add_argument('--disable-gpu')
options.add_argument("--disable-extensions")
options.add_argument("--proxy-server='direct://'")
options.add_argument("--start-maximized")
options.add_argument("--proxy-bypass-list=*")
# options.add_argument('--headless')
options.add_argument('--disable-dev-shm-usage')
options.add_argument('--ignore-certificate-errors')

driver = webdriver.Chrome(options=options)

action = ActionChains(driver)

driver.get('https://www.indeed.com/')

# User Input for Job Search Title as well as Job Search Location
jobTitle = input("Enter Job Search Title/Position: ")
jobLocation = input("Enter Job Search Location: ")

#Home Page Search for Indeed

hoverDiv = driver.find_element(By.CSS_SELECTOR, '#jobsearch > div > div.css-13s6tc1.eu4oa1w0 > div.css-1jk1vg0.eu4oa1w0 > div > div > span')
jobTitleInput = driver.find_element(By.CSS_SELECTOR, '#text-input-what')
jobLocationInput = driver.find_element(By.CSS_SELECTOR, '#text-input-where')
jobSearchButton = driver.find_element(By.CSS_SELECTOR, '#jobsearch > div > div.css-169igj0.eu4oa1w0 > button')
    

action.send_keys_to_element(jobTitleInput, jobTitle).perform()

#Hovers Over Location Bar and Presses delete button to clear text box
action.move_to_element(hoverDiv).click().perform()
clearLocationInput = driver.find_element(By.CSS_SELECTOR, '#jobsearch > div > div.css-13s6tc1.eu4oa1w0 > div.css-1jk1vg0.eu4oa1w0 > div > div > span > span.css-16oh2fs.e6fjgti0 > button')
action.move_to_element(hoverDiv).click(clearLocationInput).perform()

#Sends Job Location Search Bar Input Keys and Searches
action.send_keys_to_element(jobLocationInput, jobLocation).perform()
jobSearchButton.click()

#Set Search Settings .. Sets Experience Level to Entry level and Sets Job Type to Internship **Can turn into one function**
experienceLevel = driver.find_element(By.CSS_SELECTOR, '#filter-explvl')
action.move_to_element(experienceLevel).click(experienceLevel).perform()
levels = driver.find_elements(By.CSS_SELECTOR, '#filter-explvl-menu > li')

for level in levels:
    if level.text[:11] == 'Entry Level':
        action.click(level).perform()
        break

jobType = driver.find_element(By.CSS_SELECTOR, '#filter-jobtype')
action.move_to_element(jobType).click(jobType).perform()
roles = driver.find_elements(By.CSS_SELECTOR, '#filter-jobtype-menu > li')

for role in roles:
    if role.text[:10] == 'Internship':
        action.click(role).perform()
        break

#Gather Actual Data (Company Name : Job Title : Application Link (.get_attribute('joburl')
companyNames = []
jobTitles = []
applicationLinks = []

slides = driver.find_elements(By.CSS_SELECTOR, 'li.css-5lfssm.eu4oa1w0')

i = 1
#Scrapes Company Names, Job Titles and Application Links and appends to above lists
for slide in slides:
    try:
        jobTitleInfo = driver.find_element(By.CSS_SELECTOR, '#mosaic-provider-jobcards > ul > li:nth-child(' + str(i) + ') > div.cardOutline > div.slider_container.css-8xisqv.eu4oa1w0 > div > div.slider_item.css-kyg8or.eu4oa1w0 > div > table.jobCard_mainContent.big6_visualChanges > tbody > tr > td > div.e37uo190 > h2 > a > span')
        companyNameInfo = driver.find_element(By.CSS_SELECTOR, '#mosaic-provider-jobcards > ul > li:nth-child(' + str(i) + ') > div.cardOutline > div.slider_container.css-8xisqv.eu4oa1w0 > div > div.slider_item.css-kyg8or.eu4oa1w0 > div > table.jobCard_mainContent.big6_visualChanges > tbody > tr > td > div.company_location > div > span')
        jobTitles.append(jobTitleInfo.text)
        companyNames.append(companyNameInfo.text)
        
        moreInfoPage = driver.find_element(By.CSS_SELECTOR, '#mosaic-provider-jobcards > ul > li:nth-child(' + str(i) + ') > div.cardOutline > div.slider_container.css-8xisqv.eu4oa1w0 > div > div.slider_item.css-kyg8or.eu4oa1w0 > div > table.jobCard_mainContent.big6_visualChanges > tbody > tr > td > div.e37uo190 > h2 > a')   
        applicationLinks.append(moreInfoPage.get_attribute('href'))
                  
    except NoSuchElementException:
        pass
    i += 1

#Fills information gathered from indeed and stores within Google Sheets sheet titled Job Postings Information
sh = gc.open('Job Postings Information')
worksheet = sh.sheet1
worksheet.update_cell(1, 1, 'Company Name')
worksheet.update_cell(1, 2, 'Job Title')
worksheet.update_cell(1, 3, 'Application Link')


#Updates Sheets Cells with lists scraped from website
for i in range(2, len(companyNames) + 2):
    worksheet.update_cell(i, 1, companyNames[i - 2])
    worksheet.update_cell(i, 2, jobTitles[i - 2])
    worksheet.update_cell(i, 3, applicationLinks[i - 2])


