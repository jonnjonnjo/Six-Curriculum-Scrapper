from selenium import webdriver
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.common.by import By
from selenium.webdriver.support.wait import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import ElementNotInteractableException
import json
from selenium.webdriver.support.ui import Select
from dotenv import load_dotenv
import os

driver = webdriver.Chrome()
driver.get('https://six.itb.ac.id')
login_button = driver.find_element(By.ID,'login')

login_button.click()
load_dotenv('.env')

try:
    element = WebDriverWait(driver,1000).until(
        EC.presence_of_element_located((By.XPATH, "//a[@class='btn btn-primary loginlink']"))
    )
finally:
    print("Login with itb aaccount found")

login_with_itb_account = driver.find_element(By.XPATH, "//a[@class='btn btn-primary loginlink']")
login_with_itb_account.click();

try:
    element = WebDriverWait(driver,1000).until(
        EC.presence_of_element_located((By.ID,  "i0116"))
    )
finally:
    print("Input found")

fill_form = driver.find_element(By.ID, "i0116") 

nim = os.getenv("NIM")
print("HERE",nim)
str_nim = nim + "@mahasiswa.itb.ac.id"
fill_form.send_keys(str_nim)

next_button = driver.find_element(By.ID, "idSIButton9") 
next_button.click()


try:
    element = WebDriverWait(driver,1000).until(
        EC.presence_of_all_elements_located((By.ID,  "i0118"))
    )
finally:
    print("Input password found")

fill_form = driver.find_element(By.ID, "i0118") 
password = os.getenv("sixPassword")
fill_form.send_keys(password)


sign_in = driver.find_element(By.ID, "idSIButton9")  # Re-find after staleness
#sign_in.click()

element = WebDriverWait(driver,100000).until(EC.presence_of_element_located((By.XPATH, "//a[@class='dropdown-toggle' and contains(text(), 'Jonathan Arthurito Aldi Sinaga')]")))

driver.get("https://six.itb.ac.id/app/mahasiswa:"+nim+"/kurikulum/struktur")

en_button = element = driver.find_element(By.XPATH, "//li/a[@href='/pub/locale/en?returnTo=/app/mahasiswa:"+nim+"/kurikulum/struktur' and @title='English']")
en_button.click()
driver.refresh()

#-------------------------- START SCRAPPING

select_element_year = driver.find_element(By.ID,"th_kur")
select = Select(select_element_year)
options = select.options

data = []




for y in options:
    text = y.text
    value = y.get_attribute('value')
    data.append({"year":value})   




# iterate through each year
for each_year in data:
    year = each_year['year']
    select_element = driver.find_element(By.ID, "th_kur")
    select = Select(select_element)
    select.select_by_value(year)
    
    select_faculty = driver.find_element(By.ID,"fakultas")
    select = Select(select_faculty)
    options = select.options

    list_faculty = []

    for y in options:
        text = y.text
        if(text == ""):
            continue
        list_faculty.append({"fakultas":text})

    each_year['list_fakultas'] = list_faculty  
    
    for y in list_faculty:
        faculty = y['fakultas']
        select_faculty = driver.find_element(By.ID,"fakultas")
        select = Select(select_faculty)
        select.select_by_value(faculty)

        select_major = driver.find_element(By.ID,"prodi")   
        select = Select(select_major)
        options = select.options
        list_major = []
        
        for x in options:
            prodi = x.text;
            if(prodi == ""):
                continue;
            nim = x.get_attribute('value')  
            list_major.append({"prodi":prodi,"nim":nim})    
        
        y['list_prodi'] = list_major    
        
        
        for each_major in list_major:
            major_nim = each_major['nim']
            select_major = driver.find_element(By.ID,"prodi")
            select = Select(select_major)
            select.select_by_value(major_nim)

            # take all big table
            tbody = driver.find_element(By.TAG_NAME,'tbody')

            # Handle if tbody is empty ?
            rows = tbody.find_elements(By.TAG_NAME,'tr')

            all_courses = []
            currentSemester = 1

            if(len(rows) == 1):
                continue

            for row in rows:
                if "warning" in row.get_attribute("class"): 
                    semester_text = row.find_element(By.TAG_NAME, "th").text  
                    currentSemester = semester_text.split()[-1]  # Extract semester number
                elif((len(row.find_elements(By.TAG_NAME,"th")) == 8) or (len(row.find_elements(By.TAG_NAME,"th")) == 4)):
                    continue
                
                find_all_td = row.find_elements(By.TAG_NAME,'td')

                if(len(find_all_td) >= 3):
                    course_code = find_all_td[0].text
                    course_name = find_all_td[1].text
                    credit =  find_all_td[2].text
                    semester = currentSemester
                    compulsory = 1;

                    # find prequisite
                    all_courses.append({"course_code":course_code,"course_name":course_name,"credit":credit,"semester":semester,"compulsory":compulsory})      

                if(len(find_all_td) >= 6):
                    course_code = find_all_td[3].text
                    course_name = find_all_td[4].text   
                    credit = find_all_td[5].text
                    semester = str(int(semester) + 1)
                    all_courses.append({"course_code":course_code,"course_name":course_name,"credit":credit,"semester":semester,"compulsory":compulsory})   

            # Find the elective course

            elective_tab = driver.find_element(By.ID,'pilihan-tab')
            elective_tab.click()

            tbody = driver.find_elements(By.TAG_NAME,'tbody')
            tbody = tbody[1]
            rows = tbody.find_elements(By.TAG_NAME,'tr')    

            for row in rows:
                if(len(row.find_elements(By.TAG_NAME,"th")) == 5):
                    continue
                find_all_td = row.find_elements(By.TAG_NAME,'td')   

                if(len(find_all_td) == 4):
                    course_code = find_all_td[0].text   
                    course_name = find_all_td[1].text   
                    credit = find_all_td[2].text
                    semester = find_all_td[3].text  
                    all_courses.append({"course_code":course_code,"course_name":course_name,"credit":credit,"semester":semester,"compulsory":0})

            each_major['courses'] = all_courses 

                    



        




with open('data.json','w') as f:
    json.dump(data,f,indent=4)








holder = input("Press Enter to close the browser...")
