import requests
from bs4 import BeautifulSoup
import schedule
import time
import os
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.support.ui import WebDriverWait
from selenium.common.exceptions import StaleElementReferenceException
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.ui import Select

# Website URL to monitor
url = "https://osaka.pokemon-cafe.jp/reserve/step1" # for Osaka
# url = "https://reserve.pokemon-cafe.jp/reserve/step1" # for Tokyo

# Mailgun API key and domain
mg_api_key = os.environ.get("MG_API_KEY")
mg_domain = os.environ.get("MG_DOMAIN", "mg.vlucaswang.com")
recipient_email = os.environ.get("RECIPIENT_EMAIL", "nkwdwxc@gmail.com")
num_of_guests = 4

# Function to check for available spots
def check_availability():
    try:
        # Use Selenium to automate form submission and retrieve the updated page
        service = Service(
            executable_path=r'./chromedriver'
        )
        options = webdriver.ChromeOptions()
        options.add_experimental_option("detach", True)
        driver = webdriver.Chrome(
            service=service, options=options
        )  # Specify the path to chromedriver
        driver.implicitly_wait(5)
        driver.get(url)

        select = Select(driver.find_element(By.NAME, 'guest'))
        select.select_by_index(num_of_guests)
        driver.find_element(By.XPATH, "//*[contains(text(), '次の月を見る')]").click()

        # Wait for the page to load and elements to be ready
        WebDriverWait(driver, 10).until(
            EC.presence_of_element_located((By.CSS_SELECTOR, ".calendar-day-cell"))
        )

        # Check if the updated page indicates availability
        soup = BeautifulSoup(driver.page_source, "html.parser")
        # Find all calendar-day-cell elements
        calendar_cells = soup.find_all("li", class_="calendar-day-cell")

        # Check each calendar cell for availability
        available_slots = []
        for cell in calendar_cells:
            if "full" not in cell.text.lower() and "n/a" not in cell.text.lower():
                available_slots.append(cell.text.strip())

        if available_slots:
            send_email_notification(available_slots)
        else:
            print("No available slots found.")

    except StaleElementReferenceException:
        print("Stale Element Reference Exception. Retrying...")
        # Check if the updated page indicates availability
        soup = BeautifulSoup(driver.page_source, "html.parser")
        # Find all calendar-day-cell elements
        calendar_cells = soup.find_all("li", class_="calendar-day-cell")

        # Check each calendar cell for availability
        available_slots = []
        for cell in calendar_cells:
            if "full" not in cell.text.lower() and "n/a" not in cell.text.lower():
                available_slots.append(cell.text.strip())

        if available_slots:
            send_email_notification(available_slots)
        else:
            print("No available slots found.")

    except Exception as e:
        print(f"An error occurred: {str(e)}")
        send_error_notification(str(e))

    finally:
        driver.quit()  # Always quit the driver to close the browser

    print("Finish Running")  # Print "Finish Running" when the function finishes


# Function to send an email notification for errors
def send_error_notification(error_message):
    try:
      requests.post(
        f"https://api.mailgun.net/v3/{mg_domain}/messages",
        auth=("api", mg_api_key),
        data={"from": f"Lucas <mailgun@{mg_domain}>",
          "to": [recipient_email],
          "subject": "Error on Pokemon Cafe Reservation Script",
          "text": f"An error occurred: {error_message}"})
    except Exception as e:
        print(f"Error notification email error: {str(e)}")


# Function to send an email notification for available slots
def send_email_notification(available_slots):
    try:
      requests.post(
        f"https://api.mailgun.net/v3/{mg_domain}/messages",
        auth=("api", mg_api_key),
        data={"from": f"Lucas <mailgun@{mg_domain}>",
          "to": [recipient_email],
          "subject": "New spots available on Pokemon Cafe Reservation(Osaka)!",
          "text": f"New spots are available on the following dates in Osaka:\n\n{', '.join(available_slots)}\n\nVisit the website to reserve now! https://osaka.pokemon-cafe.jp/reserve/step1"})
    except Exception as e:
        print(f"Email notification error: {str(e)}")

# Schedule the script to run at regular intervals (e.g., every 30 minutes)
schedule.every(5).minutes.do(check_availability)
schedule.every().day.at("18:00", "Asia/Tokyo").do(check_availability)
schedule.every().day.at("18:20", "Asia/Tokyo").do(check_availability)
schedule.every().day.at("18:40", "Asia/Tokyo").do(check_availability)
schedule.every().day.at("19:00", "Asia/Tokyo").do(check_availability)

# Keep the script running
while True:
    schedule.run_pending()
    time.sleep(1)