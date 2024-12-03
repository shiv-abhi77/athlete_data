from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.support.ui import Select
from pymongo import MongoClient  # MongoDB library

# Set up MongoDB connection
client = MongoClient("mongodb://localhost:27017/")  # Update with your MongoDB URI if needed
db = client["worldathletedataset"]  # Database name
collection = db["athletes_data"]  # Collection name

# Set up Selenium WebDriver
service = Service("D:\\chromedriver-win64\\chromedriver.exe")  # Update with the correct path
driver = webdriver.Chrome(service=service)

# Open the website
url = "https://worldathletics.org/athletes"
driver.get(url)

# Allow time for dynamic content to load
driver.implicitly_wait(10)

try:
    # Locate the dropdown or element with ID 'countryCode'
    countries_dropdown = driver.find_element(By.ID, 'countryCode')  # Ensure this ID exists on the page
    
    # Use the Select class to interact with the dropdown
    select = Select(countries_dropdown)
    all_options = select.options  # Retrieve all options in the dropdown

    for option in all_options:
        country_name = option.text
        print(f"Scraping data for Country: {country_name}")
        
        # Select the country
        select.select_by_visible_text(country_name)
        
        # Wait for the table to update (if dynamic)
        driver.implicitly_wait(5)

        # Locate the table with class name 'AthleteSearch_table'
        try:
            # Locate the table
            table = driver.find_element(By.CSS_SELECTOR, "[class*='AthleteSearch_table']")
            rows = table.find_elements(By.TAG_NAME, 'tr')  # Find all rows in the table

            athlete_list = []  # List to store athlete names and URLs
            
            for row in rows:
                # Get the link inside the first column of the row
                try:
                    athlete_link = row.find_element(By.TAG_NAME, 'a')
                    athlete_name = athlete_link.text.strip()  # Extract athlete's name
                    athlete_href = athlete_link.get_attribute('href')  # Extract href value

                    # Save data into a list
                    athlete_list.append({
                        "name": athlete_name,
                        "url": athlete_href,
                        "country": country_name
                    })
                    
                    print(f"Found Athlete: {athlete_name}, URL: {athlete_href}")

                except Exception as e:
                    print(f"Failed to process a row: {e}")

            # Insert the list of athletes into MongoDB
            if athlete_list:
                collection.insert_many(athlete_list)
                print(f"Inserted {len(athlete_list)} athletes for {country_name} into the database.")

        except Exception as e:
            print(f"No table data found for {country_name}: {e}")

except Exception as e:
    print(f"An error occurred: {e}")

finally:
    # Close the browser
    driver.quit()
    client.close()  # Close MongoDB connection
