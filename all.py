from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.service import Service
from webdriver_manager.chrome import ChromeDriverManager
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
import time
import os
from pathlib import Path
import urllib3
import shutil

http = urllib3.PoolManager(timeout=urllib3.util.timeout.Timeout(connect=6000, read=6000))


# Download timing configuration (seconds)
DOWNLOAD_START_TIMEOUT = 60      # time to wait for download to start (new file appears)
DOWNLOAD_COMPLETE_TIMEOUT = 300  # time to wait for download to finish after it started

download_dir = os.path.join(os.getcwd(), "exports") # Example: a folder named 'my_downloads' in the current working directory
# Ensure the directory exists
if not os.path.exists(download_dir):
    os.makedirs(download_dir)

chrome_options = Options()
# Use Chrome preferences to control downloads (more reliable than CLI args)
prefs = {
    "download.default_directory": download_dir,  # Set your download directory
    "download.prompt_for_download": False,
    "download.directory_upgrade": True,
    "safebrowsing.enabled": True,
}
chrome_options.add_experimental_option("prefs", prefs)
chrome_options.add_argument("--disable-extensions")  # Disable extensions for better performance
chrome_options.add_argument("--disable-gpu")  # Disable GPU acceleration (optional)
chrome_options.add_argument("--no-sandbox")  # Disable the sandbox mode (if required)

# Set custom timeouts for network requests
chrome_options.add_argument("--timeout=600000")  # Allow 166+ hours for network requests (for large downloads)
#options.add_argument("download.default_directory=C:/Downloads")
# Set up ChromeDriver using Service and webdriver_manager
service = Service(ChromeDriverManager().install())  # Automatically download the correct chromedriver
driver = webdriver.Chrome(service=service, options=chrome_options)
#driver.implicitly_wait(6000)  # Implicit wait for element searches

# Increase the timeout for page loading
driver.set_page_load_timeout(600)  # Timeout set to 10 minutes for page loads
driver.set_script_timeout(600)  # Timeout set to 10 minutes for scripts

#driver.command_executor.set_timeout(6000)  # Timeout set to 100 minutes for commands

# Open the login page
driver.get("http://172.27.1.158:9090/HCRISWeb/login.do")

# Wait for the login page to load
time.sleep(2)

# Locate the email and password fields by their ID and enter the login credentials
email_field = driver.find_element(By.ID, "username")  # ID based on your inspection
password_field = driver.find_element(By.NAME, "password")  # Based on the image
login_button = driver.find_element(By.CLASS_NAME, "login100-form-btn")  # Assuming the login button is a submit button

# Enter your credentials
email_field.send_keys("admin@ontash.net")  # Replace with your actual email
password_field.send_keys("adminindia")  # Replace with your actual password

# Submit the login form (Click the login button)
login_button.click()

# Wait for the next page to load after login (adjust if necessary)
time.sleep(5)

# Now that you're logged in, navigate to the target page
driver.get("http://172.27.1.158:9090/HCRISWeb/summary.do?providerNumber=070025")

# Function to find record number for a specific provider number and fiscal year
def find_record_numbers(provider_number, fiscal_year):
    # Find all rows in the table
    rows = driver.find_elements(By.XPATH, "//table[@id='data']//tbody//tr")
    
    # Loop through the rows and search for matching provider number and fiscal year
    record_numbers = []

    for row in rows:
        provider = row.find_element(By.XPATH, ".//td[1]").text  # Provider Number is in the first column
        fiscal = row.find_element(By.XPATH, ".//td[3]").text  # Fiscal Year is in the third column
        
        if provider == provider_number and fiscal == fiscal_year:
            # If we find the matching row, get the Record Number from the second column
            record_number = row.find_element(By.XPATH, ".//td[2]").text

            last_cell_value = row.find_elements(By.TAG_NAME, "td")[-1].text
            print(last_cell_value)

            zip_link=row.find_element(By.XPATH, ".//td[6]/a").get_attribute("href")
            record_numbers.append({
                'record_number': record_number,
                'last_cell_value': last_cell_value,
                'link':zip_link  # Add the last cell value to the list
            })
    return record_numbers

# Example: Provider Number = "100122" and Fiscal Year = "03/31/2021"
provider_number = "070025"
fiscal_year = "09/30/1998"

rows = driver.find_elements(By.XPATH, "//table[@id='data']//tbody//tr")
#columns = rows[0].find_elements(By.TAG_NAME, "td")

print("start")
try:
    for row in rows:
        columns = row.find_elements(By.TAG_NAME, "td")
        provider = columns[0].text
        fiscal = columns[2].text

        #print(provider, fiscal)

        if provider == provider_number and fiscal == fiscal_year:
            print("Found matching row:")
            link = columns[5].find_element(By.TAG_NAME, "a")

            # create a new folder with name 
            version = columns[6].text
            print("version", version)
            folder_name = os.path.join(f"{provider_number}_{fiscal_year.replace('/', '-')}", f"{version}")
            folder_path = os.path.join(os.getcwd(), folder_name)
            if not os.path.exists(folder_path):
                os.makedirs(folder_path)

            try:
                link.click()
            except Exception as e:
                print(f"Time out but we'll ignore it: {e}")
                continue


            time.sleep(2)

            ok_button = WebDriverWait(driver, 6000).until(
                EC.element_to_be_clickable((By.ID, "okbutton"))
            )

            # move the downloaded file to the folder with version name
            file_name = os.listdir(download_dir)[0]
            source_file = os.path.join(download_dir, file_name)
            dest_file = os.path.join(folder_path, file_name)

            

            shutil.move(source_file, dest_file)
            
            time.sleep(2)

            ok_button.click()
except Exception as e:
    print("error")
    print(f"An error occurred: {e}")

print("over")

time.sleep(1000)

# Find the corresponding Record Number
# record_numbers = find_record_numbers(provider_number, fiscal_year)

# if record_numbers:

#     initial_handles = driver.window_handles
#     # Construct the URL for the Workbooks link
#     for record in record_numbers:

#         #record number
#         record_number=record['record_number']
#         #Dataset
#         dataset = record['last_cell_value']

#         click_link=record['link']

#         click_link.click()
        
        
#         # Construct the URL for the Workbooks link
#         #workbook_url = f"http://172.27.1.158:9090/HCRISWeb/worksheet.do?providerNumber={provider_number}&fiscalyear={fiscal_year}&recnm={record_number}"
#         #workbook_url = f"zipSheet.do?recNum={record_number}&amp;dataset={dataset}"

#          #driver.execute_script(f"window.open('{workbook_url}', '_blank');")
#         time.sleep(2)  # Wait for the new tab to open

#         if "zipSheet.do" in driver.current_url:
#             print(f"Processing tab with URL: {driver.current_url}")
#         else:
#             print(f"Skipping tab {handle} because it's not a worksheet.do page")    
