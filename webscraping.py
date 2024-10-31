import requests
from selenium import webdriver
from bs4 import BeautifulSoup
import os
import shutil
import urllib.parse
import time
# Function to download image from URL
def download_image(url, folder):
    # Create folder if it doesn't exist
    if not os.path.exists(folder):
        os.makedirs(folder)
    # Get the image name from the URL
    image_name = os.path.join(folder, os.path.basename(url))
    # Download the image
    with requests.get(url, stream=True) as response:
        with open(image_name, 'wb') as out_file:
            shutil.copyfileobj(response.raw, out_file)

# Pinterest search URL
search_url = "https://www.pinterest.com/search/pins/?q=Tom%20and%20jerry%20photos"

# Initialize a Selenium WebDriver (ensure you have chromedriver installed)
driver = webdriver.Chrome()

# Open Pinterest search URL
driver.get(search_url)

# Function to scroll to the bottom of the page
def scroll_to_bottom(driver):
    # Scroll to the bottom of the page
    driver.execute_script("window.scrollTo(0, document.body.scrollHeight);")
    # Wait for the page to load
    time.sleep(2)  # Adjust sleep time as needed

# Initialize variables
max_images = 100  # Maximum number of images to download
images_downloaded = 0
image_urls = set()

# Keep scrolling until max images are downloaded or timeout is reached
timeout = 120  # Timeout in seconds
start_time = time.time()
while images_downloaded < max_images:
    # Scroll to the bottom
    scroll_to_bottom(driver)
    
    # Get the page source
    page_source = driver.page_source
    
    # Parse the HTML content
    soup = BeautifulSoup(page_source, 'html.parser')
    
    # Find all image elements
    image_elements = soup.find_all('img')
    
    # Extract image URLs
    for img in image_elements:
        # Get the image URL
        image_url = img['src']
        # Decode URL if it is encoded
        image_url = urllib.parse.unquote(image_url)
        # Check if the URL is valid
        if image_url.startswith('http'):
            # Add the URL to the set
            image_urls.add(image_url)
    
    # Update the number of images downloaded
    images_downloaded = len(image_urls)
    
    # Check if timeout is reached
    if time.time() - start_time > timeout:
        break

# Close the browser
driver.quit()

# Download the images
for url in image_urls:
    download_image(url, "Tom_and_Jerry_Images")

print("Images downloaded successfully.")
