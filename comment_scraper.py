# InstaSentry: URL Submission, comment list selection

# Instagram Login [Delete before final product]
# Username: instasentry
# Pass: 1234567!

# Instagram political test link: https://www.instagram.com/p/DV6uGIQCdY-/
# Instagram NASA test link: https://www.instagram.com/p/DVRbpdJCW7Z/
# Note: NOT A POLITICAL EXAMPLE! Uses repetitive keywords, some examples of bots, emojis. A good sample!

from selenium import webdriver
from selenium.webdriver.common.by import By
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
        driver.maximize_window()
        driver.get("https://www.instagram.com/accounts/login/")
        time.sleep(3)

        print("\nInstagram login page opened successfully in a browser.") 
        input("After logging in, press ENTER here to continue...")
        
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

# FIND COMMENT CANDIDATES USING TIMESTAMPS
def find_comment_candidates(container):
    try:
        time_elements = container.find_elements(By.TAG_NAME, "time")

        print(f"\nTimestamp elements found: {len(time_elements)}")
        return time_elements

    except Exception as e:
        print(f"\nError: Could not locate timestamp elements. {e}")
        return []


# PRINT FIRST FEW COMMENT CANDIDATE SAMPLES
def print_comment_candidate_samples(time_elements, sample_count=10):
    try:
        print("\n--- COMMENT CANDIDATE SAMPLES ---")

        seen_text = set()
        printed = 0

        for time_element in time_elements:
            try:
                candidate_block = time_element.find_element(
                    By.XPATH,
                    "./ancestor::div[count(.//time)=1][3]"
                )

                block_text = candidate_block.text.strip()

                if block_text == "":
                    continue

                if block_text in seen_text:
                    continue

                seen_text.add(block_text)
                printed += 1

                print(f"\nCandidate {printed}:")
                print(block_text)

                if printed >= sample_count:
                    break

            except Exception:
                continue

        if printed == 0:
            print("No usable comment candidates printed.")

    except Exception as e:
        print(f"\nError: Could not print comment candidate samples. {e}")

# FIND COMMENTS CONTAINER
def find_comments_container(driver):
    try:
        time.sleep(5)

        containers = driver.find_elements(By.XPATH, "//main")

        print(f"\nMain containers found: {len(containers)}")

        if len(containers) == 0:
            return None

        return containers[0]

    except Exception as e:
        print(f"\nError: Could not locate comments container. {e}")
        return None

# EXTRACT STRUCTURED TOP-LEVEL COMMENTS
def extract_top_level_comments(time_elements, sample_limit=20):
    try:
        comments = []
        seen = set()

        for time_element in time_elements:
            try:
                candidate_block = time_element.find_element(By.XPATH,
                    "./ancestor::div[count(.//time)=1][3]")

                block_text = candidate_block.text.strip()

                if block_text == "":
                    continue

                if block_text in seen:
                    continue

                seen.add(block_text)

                lines = [line.strip() for line in block_text.split("\n") if line.strip() != ""]

                if len(lines) < 3:
                    continue

                author = lines[0]
                comment_time = lines[1]
                comment_text = " ".join(lines[2:])

                comments.append({
                    "author": author,
                    "time": comment_time,
                    "text": comment_text
                })

                if len(comments) >= sample_limit:
                    break

            except Exception:
                continue

        print(f"\nStructured top-level comments extracted: {len(comments)}")
        return comments

    except Exception as e:
        print(f"\nError: Could not extract structured comments. {e}")
        return []

# PRINT STRUCTURED COMMENTS
def print_structured_comments(comments, sample_count=10):
    try:
        print("\n--- STRUCTURED TOP-LEVEL COMMENTS ---")

        max_samples = min(sample_count, len(comments))

        for i in range(max_samples):
            print(f"\nComment {i + 1}:")
            print(f"Author: {comments[i]['author']}")
            print(f"Time:   {comments[i]['time']}")
            print(f"Text:   {comments[i]['text']}")

    except Exception as e:
        print(f"\nError: Could not print structured comments. {e}")

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

    comments_container = find_comments_container(driver)

    if comments_container is None:
        print("No comments container found.")
    else:
        time_elements = find_comment_candidates(comments_container)

        if len(time_elements) == 0:
            print("No timestamp-based comment candidates found.")
        else:
            print("Timestamp-based comment candidate test successful.")

        comments = extract_top_level_comments(time_elements, sample_limit=20)

        if len(comments) == 0:
            print("No structured top-level comments extracted.")
        else:
            print_structured_comments(comments, sample_count=10)
            
    # Browser open temp
    time.sleep(240) # 4 min
    driver.quit() 

if __name__ == "__main__":
    main()