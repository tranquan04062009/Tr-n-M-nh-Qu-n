import facebook
import random
import string
import requests
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import TimeoutException

# Replace with your own Facebook access token
access_token = 'YOUR_FACEBOOK_ACCESS_TOKEN'

# Initialize the Facebook API
graph = facebook.GraphAPI(access_token=access_token)

# Function to create a random Facebook page
def create_facebook_page():
    # Generate a random page name
    page_name = ''.join(random.choices(string.ascii_lowercase + string.digits, k=10))
    
    # Create the Facebook page
    page = graph.put_object(parent_object='me', connection_name='accounts', name=page_name)
    
    return page['id']

# Function to buff the follower count and like count of a Facebook page
def buff_facebook_page(page_id):
    # Buff the follower count using the Facebook Graph API
    graph.put_object(page_id, 'followers', method='POST')
    
    # Buff the like count using the Facebook Graph API
    graph.put_object(page_id, 'likes', method='POST')

    # Buff the follower count using the Selenium WebDriver
    driver = webdriver.Chrome()
    driver.get(f"https://www.facebook.com/{page_id}")
    try:
        follow_button = WebDriverWait(driver, 10).until(EC.presence_of_element_located((By.XPATH, "//div[@aria-label='Follow']")))
        follow_button.click()
    except TimeoutException:
        print("Failed to find the follow button using Selenium.")
    finally:
        driver.quit()

    # Buff the like count using the Requests library
    like_url = f"https://www.facebook.com/{page_id}/likes"
    like_response = requests.post(like_url, data={'__a': 1})
    if like_response.status_code == 200:
        print("Liked the page using Requests.")
    else:
        print("Failed to like the page using Requests.")

# Function to display the main menu
def display_menu():
    print("Welcome to Vietnamese Facebook Buffing Service!")
    print("1. Buff all created Facebook pages")
    print("2. Create a new Facebook page")
    print("3. Exit")

# Main program loop
while True:
    display_menu()
    choice = input("Enter your choice (1-3): ")

    if choice == '1':
        num_pages = int(input("Enter the number of pages to buff: "))
        for _ in range(num_pages):
            page_id = create_facebook_page()
            buff_facebook_page(page_id)
            print(f"Buffed page: {page_id}")
    elif choice == '2':
        page_id = create_facebook_page()
        print(f"Created new page: {page_id}")
    elif choice == '3':
        print("Exiting...")
        break
    else:
        print("Invalid choice. Please try again.")
