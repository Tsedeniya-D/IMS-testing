from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import Select
import time
import os

driver = webdriver.Chrome()
driver.maximize_window()

driver.get("http://127.0.0.1:8001/accounts/interns/")

# Fill basic info
driver.find_element(By.ID, "firstName").send_keys("Mahlet")
driver.find_element(By.ID, "lastName").send_keys("Test")
driver.find_element(By.ID, "age").send_keys("22")
driver.find_element(By.ID, "email").send_keys("mahlet@test.com")
driver.find_element(By.ID, "verification-code").send_keys("123456")
driver.find_element(By.ID, "id_phone").send_keys("+251912345678")

# Dropdowns
Select(driver.find_element(By.ID, "university")).select_by_visible_text("Addis Ababa University (AAU)")
driver.find_element(By.ID, "nationality").send_keys("Ethiopian")
driver.find_element(By.ID, "address").send_keys("Bole")
driver.find_element(By.ID, "city").send_keys("Addis Ababa")

Select(driver.find_element(By.ID, "educationLevel")).select_by_visible_text("Undergraduate")
driver.find_element(By.ID, "cgpa").send_keys("3.5")

Select(driver.find_element(By.ID, "department")).select_by_visible_text("Software Engineering")

driver.find_element(By.ID, "currentYear").send_keys("3rd Year")
driver.find_element(By.ID, "expectedGraduation").send_keys("2027-07")

Select(driver.find_element(By.ID, "duration")).select_by_visible_text("3 months")

driver.find_element(By.ID, "start_date").send_keys("2026-05-01")
driver.find_element(By.ID, "end_date").send_keys("2026-08-01")

# Upload files
driver.find_element(By.ID, "passportId").send_keys(os.path.abspath("passport.pdf"))
driver.find_element(By.ID, "recommendationLetter").send_keys(os.path.abspath("recommendation.pdf"))

# Submit
driver.find_element(By.CSS_SELECTOR, "button[type='submit']").click()

input("Press Enter when you want to close browser...")

driver.quit()