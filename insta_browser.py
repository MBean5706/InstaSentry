from selenium import webdriver
from selenium.webdriver.common.by import By
from config import MIN_SCROLL_DELAY, MAX_SCROLL_DELAY

import time
import win32gui
import win32con
import win32com.client
import random

# FORCE CHROME WINDOW TO FRONT
def force_window_to_front(window_title_keyword):
    try:
        matches = []

        def enum_handler(hwnd, _):
            if win32gui.IsWindowVisible(hwnd):
                title = win32gui.GetWindowText(hwnd)
                if window_title_keyword.lower() in title.lower():
                    matches.append(hwnd)

        win32gui.EnumWindows(enum_handler, None)

        if len(matches) == 0:
            return False

        hwnd = matches[0]

        shell = win32com.client.Dispatch("WScript.Shell")
        shell.SendKeys("%")

        win32gui.ShowWindow(hwnd, win32con.SW_SHOW)
        win32gui.SetForegroundWindow(hwnd)
        return True

    except Exception:
        return False

# MINIMIZE CHROME / INSTAGRAM WINDOW TO TASKBAR
def minimize_window(window_title_keyword):
    try:
        matches = []

        def enum_handler(hwnd, _):
            if win32gui.IsWindowVisible(hwnd):
                title = win32gui.GetWindowText(hwnd)
                if window_title_keyword.lower() in title.lower():
                    matches.append(hwnd)

        win32gui.EnumWindows(enum_handler, None)

        if len(matches) == 0:
            return False

        hwnd = matches[0]
        win32gui.ShowWindow(hwnd, win32con.SW_MINIMIZE)
        return True

    except Exception:
        return False

# OPEN INSTAGRAM LOGIN PAGE
def open_instagram_login():
    try:
        driver = webdriver.Chrome()
        force_window_to_front("Chrome")
        driver.get("https://www.instagram.com/accounts/login/")
        
        # Try repeatedly for up to ~1 second
        for _ in range(10):
            if force_window_to_front("Instagram"):
                break
            time.sleep(0.1)

        # FORCE CHROME WINDOW TO THE FRONT
        force_window_to_front("Instagram")

        print("Instagram login page opened successfully in a browser.")
        print("Waiting for Instagram login to complete...")

        return driver

    except Exception as e:
        print(f"Error: Failed to open Instagram login page. {e}")
        return None

# CHECK IF INSTAGRAM LOGIN IS COMPLETE
def is_instagram_logged_in(driver):
    try:
        if driver is None:
            return False

        current_url = driver.current_url.lower()

        if "accounts/login" in current_url:
            return False

        if not minimize_window("Instagram"):
            minimize_window("Chrome")

        return True

    except Exception:
        return False

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

# LOAD INSTAGRAM PROFILE PAGE
def load_profile_page(driver, username):
    try:
        profile_url = f"https://www.instagram.com/{username}/"

        driver.get(profile_url)
        time.sleep(3)

        current_page = driver.current_url

        if "instagram.com" not in current_page:
            print("\nError: Could not load the profile page.")
            return False

        # CHECK FOR INVALID / UNAVAILABLE PAGE
        try:
            page_text = driver.find_element(By.TAG_NAME, "body").text.lower()

            invalid_markers = [
                "sorry, this page isn't available",
                "sorry, this page isnt available",
                "the link you followed may be broken",
                "page isn't available",
                "page isnt available"
            ]

            for marker in invalid_markers:
                if marker in page_text:
                    print("\nError: Invalid username or unavailable Instagram page.")
                    return False

        except Exception:
            pass

        print("\nInstagram profile loaded successfully.")
        return True

    except Exception as e:
        print(f"\nError: Failed to load profile page. {e}")
        return False

# EXTRACT BASIC PROFILE INDICATORS
def extract_basic_profile_data(driver, username):
    try:
        time.sleep(3)

        profile_data = {
            "display_name": None,
            "username": username,
            "posts": None,
            "followers": None,
            "following": None,
            "bio": None,
            "links": None,
            "is_private": False,
            "profile_picture_present": False,
            "profile_picture_src": None,
        }

        # GET FULL PAGE TEXT
        page_text = driver.find_element(By.TAG_NAME, "body").text

        # CHECK IF PROFILE IS PRIVATE
        if "This profile is private" in page_text or "This account is private" in page_text:
            profile_data["is_private"] = True

        # CHECK PROFILE PICTURE
        try:
            profile_pic_element = driver.find_element(
                By.XPATH,
                "//section/main//header//section[1]//a/img"
            )

            profile_data["profile_picture_present"] = True
            profile_data["profile_picture_src"] = profile_pic_element.get_attribute("src")

        except Exception:
            profile_data["profile_picture_present"] = False
            profile_data["profile_picture_src"] = None

        # GET DISPLAY NAME
        try:
            display_name_element = driver.find_element(
                By.XPATH,
                "//section/main//header/div/section[2]/div[1]/div[2]/span"
            )
            text = display_name_element.text.strip()

            if text == "":
                profile_data["display_name"] = None
            else:
                profile_data["display_name"] = text
        except Exception:
            profile_data["display_name"] = None

        # GET POSTS
        try:
            post_element = driver.find_element(
                By.XPATH,
                "//section/main//header/div/section[2]/div[1]/div[3]/div[1]/span/span/span"
            )
            profile_data["posts"] = post_element.text.strip()
        except Exception:
            profile_data["posts"] = None

        # GET FOLLOWERS
        try:
            followers_element = driver.find_element(
                By.XPATH,
                "//section/main//header/div/section[2]/div[1]/div[3]/div[2]/a/span/span/span"
            )
            profile_data["followers"] = followers_element.text.strip()
        except Exception:
            profile_data["followers"] = None

        # GET FOLLOWING
        try:
            following_element = driver.find_element(
                By.XPATH,
                "//section/main//header/div/section[2]/div/div[3]/div[3]/a/span/span/span"
            )
            profile_data["following"] = following_element.text.strip()
        except Exception:
            profile_data["following"] = None

        # CLICK "MORE" IN BIO IF PRESENT
        try:
            more_buttons = driver.find_elements(
                By.XPATH,
                "//section/main//header//span[normalize-space()='more']"
            )

            for more_button in more_buttons:
                if more_button.is_displayed():
                    driver.execute_script("arguments[0].scrollIntoView(true);", more_button)
                    time.sleep(0.5)
                    driver.execute_script("arguments[0].click();", more_button)
                    time.sleep(1)
                    break

        except Exception:
            pass

        # GET BIO
        try:
            bio_elements = driver.find_elements(
                By.XPATH,
                "//section/main//header/section[1]//span/div/span"
            )

            bio_text = None

            for bio_element in bio_elements:
                text = bio_element.text.strip()

                if text != "" and text.lower() != "more":
                    bio_text = text
                    break

            profile_data["bio"] = bio_text

        except Exception:
            profile_data["bio"] = None

        # GET PROFILE LINKS (IF ANY)
        try:
            link_elements = driver.find_elements(
                By.XPATH,
                "//section/main//header//a[contains(@href, 'http')]"
            )

            links = []

            for link in link_elements:
                href = link.get_attribute("href")

                # avoid empty or duplicate entries
                if href and href not in links:
                    links.append(href)

            profile_data["links"] = links if len(links) > 0 else None

        except Exception:
            profile_data["links"] = None

        print("\nBasic profile data extracted successfully.")
        return profile_data

    except Exception as e:
        print(f"\nError extracting basic profile data: {e}")
        return None

# OPEN "ABOUT THIS ACCOUNT" FROM PROFILE MENU
def open_profile_details_menu(driver):
    try:
        time.sleep(2)

        clicked_menu = False

        # TRY MENU BUTTON XPATHS
        menu_xpaths = [
            # NEW UPDATED XPATH
            "/html/body/div[1]/div/div/div[2]/div/div/div[1]/div[2]/div[2]/section/main/div/div/header/div/section[2]/div/div[1]/div[2]/div/div",

            # OLD XPATH
            "//section/main//header/div/section[2]/div[1]/div[1]/div[2]"
        ]

        for xpath in menu_xpaths:
            try:
                menu_button = driver.find_element(By.XPATH, xpath)
                driver.execute_script("arguments[0].click();", menu_button)
                time.sleep(2)
                clicked_menu = True
                break
            except Exception:
                continue

        if not clicked_menu:
            print("Could not find profile menu button.")
            return False

        clicked_about = False

        # TRY STABLE TEXT FIRST, THEN FALLBACKS
        possible_xpaths = [
            "//*[normalize-space()='About this account']",

            # PUBLIC ACCOUNT FALLBACK
            "/html/body/div[1]/div/div/div[2]/div/div/div[2]/div/div/div[1]/div[1]/div/div/div/div/div/div/div[1]/div/div[6]/div[1]",

            # PRIVATE ACCOUNT FALLBACK
            "/html/body/div[1]/div/div/div[2]/div/div/div[2]/div/div/div[1]/div[1]/div/div/div/div/div/div/div[1]/div/div[5]/div[1]/div/div/div[2]/div/div"
        ]

        for xpath in possible_xpaths:
            try:
                about_button = driver.find_element(By.XPATH, xpath)
                driver.execute_script("arguments[0].click();", about_button)
                time.sleep(2)
                clicked_about = True
                break
            except Exception:
                continue

        if not clicked_about:
            print("Could not find 'About this account' button.")
            return False

        print("\nProfile details menu opened successfully.")
        return True

    except Exception as e:
        print(f"\nError: Could not open profile details menu. {e}")
        return False

# EXTRACT "ABOUT THIS ACCOUNT" DETAILS
def extract_about_account_data(driver):
    try:
        about_data = {
            "date_joined": None,
            "account_based_in": None,
            "former_usernames": None
        }

        # GET DATE JOINED
        try:
            date_joined_element = driver.find_element(
                By.XPATH,
                "//div[contains(@aria-label, 'Date joined')]//span[2]"
            )
            about_data["date_joined"] = date_joined_element.text.strip()
        except Exception:
            about_data["date_joined"] = None

        # GET ACCOUNT BASED IN
        try:
            account_based_element = driver.find_element(
                By.XPATH,
                "//div[contains(@aria-label, 'Account based in')]//span[2]"
            )
            about_data["account_based_in"] = account_based_element.text.strip()
        except Exception:
            about_data["account_based_in"] = None

        # GET FORMER USERNAMES
        try:
            row = driver.find_element(
                By.XPATH,
                "//div[contains(@aria-label, 'Former usernames')]"
            )

            text = row.get_attribute("aria-label")

            if text:
                about_data["former_usernames"] = text.replace("Former usernames", "").strip()
            else:
                about_data["former_usernames"] = None

        except Exception:
            try:
                # Fallback to full xpath
                element = driver.find_element(
                    By.XPATH,
                    "/html/body/div[4]/div[1]/div/div[2]/div/div/div/div/div/div/div/div/div[1]/div/div/div[2]/div/div/div[2]/div[3]/div[2]/div[1]"
                )
                about_data["former_usernames"] = element.text.strip()
            except Exception:
                about_data["former_usernames"] = None

        print("\nAbout-this-account data extracted successfully.")
        return about_data

    except Exception as e:
        print(f"\nError extracting about-this-account data: {e}")
        return None

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
