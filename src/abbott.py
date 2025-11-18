import time
import os
from pathlib import Path
from loguru import logger
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.chrome.options import Options
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()

# Credentials from environment variables
EMAIL = os.getenv("EMAIL")
PASSWORD = os.getenv("PASSWORD")

# Download folder configuration
DOWNLOAD_DIR = "/mnt/bca/mtDNA/science/temp"
LIST = "data/list.txt"

os.makedirs(DOWNLOAD_DIR, exist_ok=True)
logger.info(f"Base download folder: {DOWNLOAD_DIR}")

# Load product IDs from list.txt file
with open(LIST, "r") as f:
    product_ids = [line.strip() for line in f if line.strip()]

logger.info(f"Loaded {len(product_ids)} product IDs from {LIST}")

# Set up Chrome options for automatic downloads
chrome_options = Options()
chrome_options.add_experimental_option("prefs", {
    "download.default_directory": DOWNLOAD_DIR,
    "download.prompt_for_download": False,
    "download.directory_upgrade": True,
    "safebrowsing.enabled": True
})

def wait_for_download_and_rename(base_folder: str, product_id: str, timeout: int = 600) -> bool:
    """Wait for download to complete and move to nested folder with product_id name.
    
    Args:
        base_folder: Path to the base download directory.
        product_id: Product ID to use for creating nested folder and renaming.
        timeout: Maximum time to wait for download in seconds.
    
    Returns:
        True if download and rename succeeded, False otherwise.
    """
    base_path = Path(base_folder)
    product_folder = base_path / product_id
    product_folder.mkdir(parents=True, exist_ok=True)
    
    start_time = time.time()
    initial_files = set(f.name for f in base_path.glob("*") if f.is_file())
    
    # Wait for download to complete
    while time.time() - start_time < timeout:
        # Get all completed files (not currently downloading)
        current_files = [f for f in base_path.glob("*") if f.is_file() and not f.name.endswith('.crdownload')]
        
        # Find new files that weren't there initially
        new_files = [f for f in current_files if f.name not in initial_files]
        
        if new_files:
            # Get the most recently modified new file
            latest_file = max(new_files, key=lambda x: x.stat().st_mtime)
            extension = latest_file.suffix
            new_path = product_folder / f"{product_id}{extension}"
            
            # Remove existing file with same name if it exists
            if new_path.exists():
                new_path.unlink()
            
            # Move the file to nested folder
            latest_file.rename(new_path)
            
            logger.success(f"Moved to: {product_id}/{product_id}{extension}")
            return True
        
        time.sleep(1)
    
    logger.error(f"Download timeout for {product_id}")
    return False

# Set up WebDriver
driver = webdriver.Chrome(options=chrome_options)

# Navigate to login page
driver.get("https://labcentral.corelaboratory.abbott/int/en/home.html")

# Login process
email = WebDriverWait(driver, 10).until(
    EC.presence_of_element_located((By.XPATH, "//input[@placeholder='Email Address']"))
)
email.send_keys(EMAIL)

password = WebDriverWait(driver, 10).until(
    EC.presence_of_element_located((By.XPATH, "//input[@placeholder='Password']"))
)
password.send_keys(PASSWORD)

time.sleep(5)

# Submit login
submit_button = WebDriverWait(driver, 10).until(
    EC.element_to_be_clickable((By.XPATH, "//button[@type='submit']"))
)

# Scroll the button into view to avoid interception
driver.execute_script("arguments[0].scrollIntoView({behavior: 'smooth', block: 'center'});", submit_button)
time.sleep(1)  # Short pause to ensure scroll completes

submit_button.click()

# Wait for login to complete
time.sleep(10)

# Navigate to the Vietnamese technical library search page
driver.get("https://labcentral.corelaboratory.abbott/int/vi/secure/technical-library.html#pi_search")

# Wait for page to load
time.sleep(5)

dropdown_control = WebDriverWait(driver, 10).until(
        EC.element_to_be_clickable((By.XPATH, "//div[contains(@class, 'react-select__placeholder') and text()='Chọn']/parent::div/parent::div"))
    )
dropdown_control.click()  # Click to open the menu

time.sleep(5)

# Wait for and click the "Tìm kiếm chung" option
search_option = WebDriverWait(driver, 10).until(
    EC.element_to_be_clickable((By.XPATH, "//div[contains(@class, 'react-select__option') and contains(text(), 'Tìm kiếm chung')]"))
)
search_option.click()

time.sleep(5)

# Loop through each product ID
for product_id in product_ids:
    logger.info(f"Searching for ID: {product_id}")
    
    # Check if PDF already exists in nested folder
    product_folder = Path(DOWNLOAD_DIR) / product_id
    if product_folder.exists():
        existing_files = list(product_folder.glob(f"{product_id}.*"))
        if existing_files:
            logger.info(f"File for {product_id} already exists, skipping download: {existing_files[0].name}")
            continue
    
    # Find and fill the "Số đầu dòng sản phẩm" input field
    id_field = WebDriverWait(driver, 10).until(
        EC.presence_of_element_located((By.XPATH, "//input[contains(@placeholder, 'Nhập số đầu dòng…')]"))
    )
    id_field.clear()
    id_field.send_keys(product_id)
    
    # Click the "Tìm kiếm" button
    search_button = WebDriverWait(driver, 10).until(
        EC.element_to_be_clickable((By.CSS_SELECTOR, "button.btn.search-input-submit"))
    )

    # Scroll the button into view to avoid interception
    driver.execute_script("arguments[0].scrollIntoView({behavior: 'smooth', block: 'center'});", search_button)
    time.sleep(1)  # Short pause to ensure scroll completes

    search_button.click()
    
    # Wait as per instructions
    time.sleep(5)
    
    # Find and click the PDF link
    try:
        # Click the checkbox for the row containing the product_id
        checkbox = WebDriverWait(driver, 10).until(
            EC.element_to_be_clickable((By.XPATH, f"//tr[td[contains(text(), '{product_id}')]]//span[@class='a-checkbox__custom' and @role='checkbox']"))
        )

        # Scroll the button into view to avoid interception
        driver.execute_script("arguments[0].scrollIntoView({behavior: 'smooth', block: 'center'});", checkbox)
        time.sleep(1)  # Short pause to ensure scroll completes
        
        checkbox.click()
        
        # Wait as per instructions
        time.sleep(5)

        # Click the "Tải xuống đã chọn (N)" button robustly
        download_button = WebDriverWait(driver, 15).until(
            EC.element_to_be_clickable((By.XPATH, "//button[contains(@class,'btn') and starts-with(normalize-space(),'Tải xuống')]"))
        )

        # Scroll the button into view to avoid interception
        driver.execute_script("arguments[0].scrollIntoView({behavior: 'smooth', block: 'center'});", download_button)
        time.sleep(1)  # Short pause to ensure scroll completes

        download_button.click()

        # Wait as per instructions
        time.sleep(5)
        
        logger.debug('Clicked download button, waiting for continue button...')

        # Click "TIẾP TỤC" in the popup robustly
        continue_button = WebDriverWait(driver, 60).until(
            EC.element_to_be_clickable((By.XPATH, "//a[contains(@class, 'btn') and contains(., 'TIẾP TỤC')]"))
        )

        # Scroll the button into view to avoid interception
        driver.execute_script("arguments[0].scrollIntoView({behavior: 'smooth', block: 'center'});", continue_button)
        time.sleep(1)  # Short pause to ensure scroll completes
        
        continue_button.click()
        
        # Wait for download to complete and move to nested folder
        if wait_for_download_and_rename(DOWNLOAD_DIR, product_id, timeout=600):
            logger.success(f"Successfully downloaded and moved file for {product_id}")
        else:
            logger.warning(f"Download may have failed for {product_id}")
        
        time.sleep(2)  # Brief pause before next iteration
    except Exception as e:
        logger.error(f"No PDF found or error for {product_id}; skipping...")
        logger.exception("Traceback:")

# Clean up
driver.quit()
logger.info("Automation complete.")