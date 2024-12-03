import threading
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.service import Service
from pymongo import MongoClient

# Set up MongoDB connection
client = MongoClient("mongodb://localhost:27017/")  # Update with your MongoDB URI if needed
db = client["worldathletedataset"]  # Database name
source_collection = db["athletes_data"]  # Source collection name
target_collection = db["athletes_details"]  # Target collection name for saving scraped data

# Selenium WebDriver path
webdriver_path = "D:\\chromedriver-win64\\chromedriver.exe"  # Update with the correct path

# Function to process a chunk of athletes
def process_athletes_chunk(athletes_chunk):
    # Set up Selenium WebDriver
    service = Service(webdriver_path)
    driver = webdriver.Chrome(service=service)
    driver.implicitly_wait(10)

    try:
        for athlete in athletes_chunk:
            athlete_id = athlete["_id"]
            athlete_url = athlete["url"]

            # Open the athlete's page
            driver.get(athlete_url)
            driver.implicitly_wait(5)

            # Scrape athlete details
            athlete_details = {}

            # Name
            try:
                name_element = driver.find_element(By.CSS_SELECTOR, ".athletesBio_athletesBioTitle__3pPRL")
                athlete_details["name"] = name_element.text.strip()
            except:
                athlete_details["name"] = None

            # Events
            try:
                events_elements = driver.find_elements(By.CSS_SELECTOR, ".athletesBio_athletesBioTag__3ki57")
                athlete_details["events"] = [event.text.strip() for event in events_elements]
            except:
                athlete_details["events"] = []

            # Country
            try:
                country_element = driver.find_element(By.CSS_SELECTOR, ".athletesBio_athletesBioDetails__1wgSI:nth-child(1) .athletesBio_athletesBioTagValue__oKZC4")
                athlete_details["country"] = country_element.text.strip()
            except:
                athlete_details["country"] = None

            # Date of Birth
            try:
                dob_element = driver.find_element(By.CSS_SELECTOR, ".athletesBio_athletesBioDetails__1wgSI:nth-child(2) .athletesBio_athletesBioTagValue__oKZC4")
                athlete_details["date_of_birth"] = dob_element.text.strip()
            except:
                athlete_details["date_of_birth"] = None

            # Athlete Code
            try:
                code_element = driver.find_element(By.CSS_SELECTOR, ".athletesBio_athletesBioDetails__1wgSI:nth-child(3) .athletesBio_athletesBioTagValue__oKZC4")
                athlete_details["athlete_code"] = code_element.text.strip()
            except:
                athlete_details["athlete_code"] = None

            # Highest Event Ranking
            try:
                ranking_element = driver.find_element(By.CSS_SELECTOR, ".athletesBio_athletesBioLastResultsPlace__RUMWI")
                ranking_event_element = driver.find_element(By.CSS_SELECTOR, ".athletesBio_athletesBioLastResultsValue__2MIPM")
                athlete_details["highest_event_ranking"] = {
                    "ranking": ranking_element.text.strip(),
                    "event": ranking_event_element.text.strip()
                }
            except:
                athlete_details["highest_event_ranking"] = None

            # Scrape Athlete's Image URL
            try:
                image_container = driver.find_element(By.CSS_SELECTOR, ".athletesBio_athletesBioImageContainer__3x9PY")
                image_element = image_container.find_element(By.TAG_NAME, "img")
                athlete_details["image_url"] = image_element.get_attribute("src")
            except:
                athlete_details["image_url"] = None

            # Personal Bests
            try:
                personal_bests = []
                pb_rows = driver.find_elements(By.CSS_SELECTOR, ".personalBestsTable_row")
                for row in pb_rows:
                    try:
                        event = row.find_element(By.CSS_SELECTOR, ".personalBestsTable_event").text.strip()
                        result = row.find_element(By.CSS_SELECTOR, ".personalBestsTable_result").text.strip()
                        date = row.find_element(By.CSS_SELECTOR, ".personalBestsTable_date").text.strip()
                        score = row.find_element(By.CSS_SELECTOR, ".personalBestsTable_score").text.strip()
                        personal_bests.append({
                            "event": event,
                            "result": result,
                            "date": date,
                            "score": score
                        })
                    except:
                        continue
                athlete_details["personal_bests"] = personal_bests
            except:
                athlete_details["personal_bests"] = []

            # Additional Data from Div Elements
            try:
                events_divs = driver.find_elements(By.CSS_SELECTOR, ".athletesDropdownCard_athletesDropdownCard__2TpE2")
                additional_events = []
                for div in events_divs:
                    title = div.find_element(By.CSS_SELECTOR, ".athletesTitle_athletesTitle__388RT").text.strip()
                    details = div.find_elements(By.CSS_SELECTOR, ".athletesEventsDetails_athletesEventsDetailsContent__37Ko7")
                    result = details[0].find_element(By.CSS_SELECTOR, ".athletesEventsDetails_athletesEventsDetailsValue__FrHFZ").text.strip() if len(details) > 0 else None
                    date = details[1].find_element(By.CSS_SELECTOR, ".athletesEventsDetails_athletesEventsDetailsValue__FrHFZ").text.strip() if len(details) > 1 else None
                    score = details[2].find_element(By.CSS_SELECTOR, ".athletesEventsDetails_athletesEventsDetailsValue__FrHFZ").text.strip() if len(details) > 2 else None

                    additional_events.append({
                        "title": title,
                        "result": result,
                        "date": date,
                        "score": score
                    })
                athlete_details["additional_events"] = additional_events
            except:
                athlete_details["additional_events"] = []

            # Save the scraped data into the target collection
            scraped_document = {
                "_id": athlete_id,
                "url": athlete_url,
                "details": athlete_details
            }
            target_collection.replace_one({"_id": athlete_id}, scraped_document, upsert=True)
            print(f"Saved details for athlete {athlete_id}")

    finally:
        # Close the WebDriver
        driver.quit()

# Main function to divide work into threads
def main():
    # Fetch all athlete documents
    athletes = list(source_collection.find({}, {"url": 1, "_id": 1}))
    
    # Start from index 700
    athletes = athletes[700:]  # Slice the array to include elements from index 700 onwards
    
    num_threads = 5  # Define the number of threads
    chunk_size = len(athletes) // num_threads
    threads = []

    for i in range(num_threads):
        start_index = i * chunk_size
        end_index = None if i == num_threads - 1 else (i + 1) * chunk_size
        chunk = athletes[start_index:end_index]
        thread = threading.Thread(target=process_athletes_chunk, args=(chunk,))
        threads.append(thread)
        thread.start()

    for thread in threads:
        thread.join()


if __name__ == "__main__":
    main()
