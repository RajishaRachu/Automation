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
import pandas as pd

http = urllib3.PoolManager(timeout=urllib3.util.timeout.Timeout(connect=6000, read=6000))

download_dir = os.path.join(os.getcwd(), "exports") # Example: a folder named 'my_downloads' in the current working directory

def find_files(directory, prefix):
    # List to store matched file names
    matched_files = []

    # Iterate through all files in the directory
    for filename in os.listdir(directory):
        # Check if the file starts with the specified prefix
        if filename.startswith(prefix):
            matched_files.append(filename)

    return matched_files

# files = find_files(download_dir, "10040_12-31-1996")
# print(len(files))


# Download timing configuration (seconds)
DOWNLOAD_START_TIMEOUT = 60      # time to wait for download to start (new file appears)
DOWNLOAD_COMPLETE_TIMEOUT = 300  # time to wait for download to finish after it started

# Ensure the directory exists
if not os.path.exists(download_dir):
    os.makedirs(download_dir)

chrome_options = Options()
# Use Chrome preferences to control downloads (more reliable than CLI args)
prefs = {
    "download.default_directory": download_dir,  # Set your download directory
    "download.prompt_for_download": False,
    "download.directory_upgrade": True,
    "safebrowsing.enabled": False,

}
chrome_options.add_experimental_option("prefs", prefs)
chrome_options.add_argument("--disable-extensions")  # Disable extensions for better performance
chrome_options.add_argument("--disable-gpu")  # Disable GPU acceleration (optional)
chrome_options.add_argument("--no-sandbox")  # Disable the sandbox mode (if required)
chrome_options.add_argument("--disable-web-security")  # Disable web security
chrome_options.add_argument("--disable-features=IsolateOrigins,site-per-process")  # Disable site isolation
chrome_options.add_argument("--disable-features=CertificateTransparency")





# Set custom timeouts for network requests
chrome_options.add_argument("--timeout=600000")  # Allow 166+ hours for network requests (for large downloads)
#options.add_argument("download.default_directory=C:/Downloads")
# Set up ChromeDriver using Service and webdriver_manager
service = Service(ChromeDriverManager().install())  # Automatically download the correct chromedriver
driver = webdriver.Chrome(service=service, options=chrome_options)
#driver.implicitly_wait(6000)  # Implicit wait for element searches

# Increase the timeout for page loading
driver.set_page_load_timeout(6000)  # Timeout set to 10 minutes for page loads
driver.set_script_timeout(6000)  # Timeout set to 10 minutes for scripts

driver.command_executor.set_timeout(6000)  # Timeout set to 100 minutes for commands

# Open the login page
driver.get("https://costreport.ontash.org/HCRISWeb/login.do")

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
def read_excel(file_path):
    df=pd.read_excel(file_path)
     # Convert 'Fiscal Year' column to datetime and then to MM/DD/YYYY format
    df['Fiscal Year'] = pd.to_datetime(df['Fiscal Year'], errors='coerce').dt.date  # Remove time part
    df['Fiscal Year'] = df['Fiscal Year'].apply(lambda x: x.strftime('%m/%d/%Y'))  # Format as MM/DD/YYYY
    provider_fiscal_list=df[['Provider Number','Fiscal Year']].values.tolist()
    return provider_fiscal_list

def download_worksheet(driver,provider_number, fiscal_year):
    print(provider_number,fiscal_year)
    driver.get(f"https://costreport.ontash.org/HCRISWeb/summary.do?providerNumber={provider_number}")
    rows = driver.find_elements(By.XPATH, "//table[@id='data']//tbody//tr")
    print("Starting Download - Provider:", provider_number, "Fiscal Year:", fiscal_year)
    try:
        version_suffix=0
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
                # record_number = columns[1].text
                print("version", version)
                # folder_name = os.path.join(f"{provider_number}_{fiscal_year.replace('/', '-')}", f"HCRIS_{provider_number}_{fiscal_year.replace('/', '-')}_Version_{version}")
                # folder_path = os.path.join(os.getcwd(), folder_name)
                # if not os.path.exists(folder_path):
                #     os.makedirs(folder_path)
                # else:
                #     version_suffix += 1
                #     folder_name = os.path.join(f"{provider_number}_{fiscal_year.replace('/', '-')}", f"HCRIS_{provider_number}_{fiscal_year.replace('/', '-')}_Version_{version}({version_suffix})")
                #     folder_path = os.path.join(os.getcwd(), folder_name)
                #     os.makedirs(folder_path)

                try:
                    link.click()
                except Exception as e:
                    print(f"Time out but we'll ignore it: {e}")
                    time.sleep(5)
                    print("Retrying to click the link...")
                    continue


                time.sleep(2)

                ok_button = WebDriverWait(driver, 6000).until(
                    EC.element_to_be_clickable((By.ID, "okbutton"))
                )

                # move the downloaded file to the folder with version name
                # downloaded_filename = f"{provider_number}_{fiscal_year.replace('/', '-')}"
                # downloaded_filename = downloaded_filename.lstrip("0")  # Remove leading zeros
                # print("downloaded_filename", downloaded_filename)

                # files = find_files(download_dir, downloaded_filename)
                # while not files:
                #     print(f"No downloaded file found for Provider: {provider_number}, Fiscal Year: {fiscal_year}! Waiting for 5 seconds and retrying...")
                #     time.sleep(5)
                #     files = find_files(download_dir, downloaded_filename)
                #     continue  # Skip to the next iteration if no file is found

                # if (len(files) > 1):
                #     print(f"Multiple downloaded files found for Provider: {provider_number}, Fiscal Year: {fiscal_year}. Using the first one.")

                # file_name = files[0]

                # source_file = os.path.join(download_dir, file_name)
                # dest_file = os.path.join(folder_path, file_name)
                # shutil.move(source_file, dest_file)

                time.sleep(2)

                okClicked = False
                while not okClicked:
                    try:
                        ok_button.click()
                        okClicked = True
                    except Exception as e:
                        print(f"Time out but we'll ignore it: {e}")
                        time.sleep(5)

                        continue
            else:
                if(f"{provider_number}_{fiscal_year}" not in no_sheet):
                    no_sheet.append(f"{provider_number}_{fiscal_year}")


        return f"Download completed for Provider: {provider_number}, Fiscal Year: {fiscal_year}"

    except Exception as e:
        print("error")
        print(f"An error occurred: {e}")
        #time.sleep(1000)

    print("Download worksheet over")

def delete_all_files(directory):
    # Iterate through all the files in the directory
    for filename in os.listdir(directory):
        file_path = os.path.join(directory, filename)

        # Check if it's a file (not a directory)
        if os.path.isfile(file_path):
            os.remove(file_path)  # Delete the file


excel_file_path="/home/user/rajisha/sample7.xlsx"
no_sheet=[]

# delete_all_files(download_dir)

provider_fiscal_list=read_excel(excel_file_path)
print(provider_fiscal_list)

for provider_number,fiscal_year in provider_fiscal_list:
    completed_message=download_worksheet(driver,str(provider_number).zfill(6), str(fiscal_year).strip())
    print("complete",completed_message)

#print(no_sheet)





time.sleep(1000)
