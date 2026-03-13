# InstaSentry: URL Submission, comment list selection

from selenium import webdriver
import time

# POST URL SUBMISSION
def get_post_url():
    while True:
        post_url= input("\nEnter the Instagram post URL: ").strip()

        if post_url == "":
            print("URL cannot be empty. Please try again.")
            continue

        if "instagram.com" not in post_url:
            print("Invalid Instagram URL. Please try again.")
            continue

        return post_url

# KEYWORD LIST SELECTION
def get_keywords():
    while True:
        keyword_input = input("\nEnter keywords to search for (comma separated): ").strip()

        if keyword_input == "":
            print("Keyword list cannot be empty. Please try again.")
            continue
        
        keywords = [
            word.strip().lower() 
            for word in keyword_input.split(",") 
            if len(word.strip()) >= 2
        ]

        if len(keywords) == 0:
            print("Keywords must be at least 2 characters long. Please try again.")
            continue

        return keywords

# EXTRACTION CONFIRMATION
def confirm_extraction():
    while True:
        choice = input("\nReady to extract comments? (Y/N): ").strip().lower()

        if choice == "y":
            print("\nLoading login window...")
            return True

        elif choice == "n":
            print("\nExtraction canceled.")
            return False

        else:
            print("Invalid input. Please enter Y or N.")

# OPEN INSTAGRAM LOGIN PAGE
def open_instagram_login():
    try: 
        driver = webdriver.Chrome()
        driver.get("https://www.instagram.com/accounts/login/")
        time.sleep(3)

        print("\nInstagram login page opened successfully in a browser.") 
        input("After logging, press ENTER here to continue...")
        
        return driver

    except Exception as e:
        print(f"\nError: Failed to open Instagram login page. {e}")
        return None

# LOAD POST AFTER LOGIN
def load_post_after_login(driver, post_url):
    try:
        driver.get(post_url)
        time.sleep(3)

        current_page = driver.current_url

        if "instagram.com" not in current_page:
            print("\nError: Could not load the Instagram post.")
            return False
        
        if current_page != post_url:
            print("\nWarning: Instagram redirected the page.")
            print("\nExpected: ", post_url)
            print("Current: ", current_page)
        
        print("\nInstagram post loaded successfully.")
        return True

    except Exception as e:
        print(f"\nError: Failed to load the Instagram post. {e}")
        return False

# TEST MAIN
def main():
    post_url = get_post_url()

    print("\nPost URL accepted: ")
    print(post_url)

    keywords = get_keywords()

    print("\nKeywords accepted:")
    print(keywords)

    if not confirm_extraction():
        return

    driver = open_instagram_login()

    if driver is None:
        print("Program stopped.")
        return
    
    post_loaded = load_post_after_login(driver, post_url)

    if not post_loaded:
        print("Program stopped.")
        driver.quit()
        return
    
    print("\nPost loaded in logged-in session.")

    # Browser open temp
    time.sleep(240)
    driver.quit() 

if __name__ == "__main__":
    main()