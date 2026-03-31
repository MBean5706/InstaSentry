from selenium import webdriver
from selenium.webdriver.common.by import By
import time
import random
from config import MIN_SCROLL_DELAY, MAX_SCROLL_DELAY

# OPEN INSTAGRAM LOGIN PAGE
def open_instagram_login():
    try: 
        driver = webdriver.Chrome()
        # driver.maximize_window()
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

# SCROLL PAGE ONCE TO LOAD MORE COMMENTS
def scroll_once_for_comments(driver):
    try:
        old_height = driver.execute_script("return document.body.scrollHeight")

        driver.execute_script("window.scrollTo(0, document.body.scrollHeight);")

        delay = random.uniform(MIN_SCROLL_DELAY, MAX_SCROLL_DELAY)
        time.sleep(delay)

        new_height = driver.execute_script("return document.body.scrollHeight")

        print(f"\nScrolled page once. Delay used: {delay:.2f} seconds")

        if new_height > old_height:
            print("Page height increased. More content may have loaded.")
        else:
            print("Page height did not increase.")

        return new_height > old_height

    except Exception as e:
        print(f"\nError: Could not scroll page for comments. {e}")
        return False

# FIND INNER SCROLLABLE CONTAINER
def find_scrollable_comment_container(driver):
    try:
        time.sleep(5)
        divs = driver.find_elements(By.XPATH, "//div")

        for div in divs:
            try:
                overflow = driver.execute_script(
                    "return window.getComputedStyle(arguments[0]).overflowY;", div
                )

                height = driver.execute_script(
                    "return arguments[0].clientHeight;", div
                )

                scroll_height = driver.execute_script(
                    "return arguments[0].scrollHeight;", div
                )

                if overflow in ["auto", "scroll"] and scroll_height > height:
                    print("\nFound a scrollable container.")
                    return div

            except Exception:
                continue

        print("\nNo scrollable container found.")
        return None

    except Exception as e:
        print(f"\nError: Could not find scrollable container. {e}")
        return None

# SCROLL INSIDE THE INNER CONTAINER
def scroll_comment_container(container):
    try:
        driver = container._parent

        old_scroll_top = driver.execute_script(
            "return arguments[0].scrollTop;", container
        )

        old_scroll_height = driver.execute_script(
            "return arguments[0].scrollHeight;", container
        )

        driver.execute_script(
            "arguments[0].scrollTop = arguments[0].scrollHeight;", container
        )

        delay = random.uniform(MIN_SCROLL_DELAY, MAX_SCROLL_DELAY)
        time.sleep(delay)

        new_scroll_top = driver.execute_script(
            "return arguments[0].scrollTop;", container
        )

        new_scroll_height = driver.execute_script(
            "return arguments[0].scrollHeight;", container
        )

        print(f"\nScrolled inner container. Delay used: {delay:.2f} seconds")

        if new_scroll_top > old_scroll_top:
            print("Inner container moved downward.")
        else:
            print("Inner container did not move.")

        return new_scroll_height > old_scroll_height or new_scroll_top > old_scroll_top

    except Exception as e:
        print(f"\nError: Could not scroll inner container. {e}")
        return False