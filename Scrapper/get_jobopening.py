import time
import os
from datetime import datetime
from selenium import webdriver
from selenium.webdriver.firefox.service import Service
from selenium.webdriver.firefox.options import Options
from webdriver_manager.firefox import GeckoDriverManager
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import TimeoutException

def track_browser():
    firefox_options = Options()

    driver = webdriver.Firefox(service=Service(GeckoDriverManager().install()), options=firefox_options)
    
    driver.execute_script("window.open('');")
    driver.switch_to.window(driver.window_handles[-1])
    
    driver.get("https://www.linkedin.com/")

    urls = []
    current_url = ""

    try:
        print("Browser window opened. You can now navigate to different pages.")
        print("The script will track your browsing. Close the browser window to stop tracking.")
        
        while True:
            try:
                new_url = driver.current_url
                if new_url != current_url:
                    current_url = new_url
                    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
                    
                    urls.append(f"{timestamp}: {current_url}")
                    print(f"Visited: {current_url}")
                    
                    # Wait for the page to be fully loaded
                    try:
                        WebDriverWait(driver, 30).until(
                            lambda d: d.execute_script('return document.readyState') == 'complete'
                        )
                        print("Page fully loaded.")
                    except TimeoutException:
                        print("Timeout waiting for page to load. Saving current state.")
                    
                    page_source = driver.page_source
                    file_name = f"HtmlPages/JobOpeningPage/{timestamp}.html"
                    os.makedirs(os.path.dirname(file_name), exist_ok=True)
                    with open(file_name, "w", encoding="utf-8") as f:
                        f.write(page_source)
                    print(f"Saved page as: {file_name}")
            except Exception as e:
                print(f"An error occurred: {str(e)}")
                print("Browser window might be closed")
                break
            
            time.sleep(1)  
    finally:
        with open("browsing_history.txt", "w") as f:
            f.write("\n".join(urls))
        print("Browsing history saved to browsing_history.txt")
        
        driver.quit()

if __name__ == "__main__":
    track_browser()