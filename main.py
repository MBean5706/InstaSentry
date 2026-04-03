# INSTASENTRY  

# Instagram test link #1: https://www.instagram.com/p/DV6uGIQCdY-/
# Instagram test link #2: https://www.instagram.com/p/DVRbpdJCW7Z/

import time
from config import MAX_COMMENTS, MAX_NO_NEW_SCROLLS
from comment_processing import (
    save_comments_to_file,
    save_data_to_json
)
from user_input import (
    get_post_url,
    get_comment_limit,
    get_keywords,
    confirm_extraction,
    get_profile_username
)
from insta_browser import (
    open_instagram_login,
    load_post_after_login,
    load_profile_page,
    find_comments_container,
    find_comment_candidates,
    scroll_once_for_comments,
    find_scrollable_comment_container,
    scroll_comment_container,
    extract_basic_profile_data,
    open_profile_details_menu,
    extract_about_account_data
)
from comment_processing import (
    extract_top_level_comments,
    print_structured_comments,
    filter_comments_by_keywords,
    print_filtered_comments
)
from analysis_scoring import (
    build_account_age_result,
    calculate_total_risk_score,
    calculate_final_score,
    build_username_changes_result,
    build_post_count_result,
    build_follower_count_result,
    build_following_count_result,
    build_following_follower_ratio_result
)

# TEST MAIN
def main():
    post_url = get_post_url()

    print("\nPost URL accepted:" , post_url)

    comment_limit = get_comment_limit()

    print("\nComment limit accepted:" , comment_limit)

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

    scroll_container = find_scrollable_comment_container(driver)

    if scroll_container is None:
        print("No scrollable container found.")
    else:
        # INITIAL LOAD
        comments_container = find_comments_container(driver)
        time_elements = find_comment_candidates(comments_container)
        print(f"\nInitial timestamps: {len(time_elements)}")

        no_new_scrolls = 0

        # LOOP SCROLLING
        while len(time_elements) < comment_limit and no_new_scrolls < MAX_NO_NEW_SCROLLS:

            before_count = len(time_elements)

            # SCROLL INNER CONTAINER
            scroll_comment_container(scroll_container)

            # REFRESH CONTAINER + ELEMENTS
            comments_container = find_comments_container(driver)
            time_elements = find_comment_candidates(comments_container)

            after_count = len(time_elements)

            print(f"\nTimestamps AFTER scroll: {after_count}")

            # CHECK IF NEW COMMENTS LOADED
            if after_count > before_count:
                print("New comments loaded.")
                no_new_scrolls = 0
            else:
                print("No new comments loaded.")
                no_new_scrolls += 1

        print(f"\nFinal total timestamps collected: {len(time_elements)}")

        # EXTRACT STRUCTURED COMMENTS
        comments = extract_top_level_comments(time_elements, sample_limit=comment_limit)

        # PRINT STRUCTURED COMMENTS
        print_structured_comments(comments, sample_count=10)

        # FILTER COMMENTS BY KEYWORDS
        filtered_comments = filter_comments_by_keywords(comments, keywords)

        # PRINT FILTERED COMMENTS
        print_filtered_comments(filtered_comments)

        # SAVE ALL COMMENTS
        save_comments_to_file(comments, "all_comments.txt")

        # SAVE FILTERED COMMENTS
        save_comments_to_file(filtered_comments, "filtered_comments.txt")

        # SAVE COMMENTS TO JSON
        save_data_to_json(comments, "all_comments.json")

        # SAVE FILTERED COMMENTS TO JSON
        save_data_to_json(filtered_comments, "filtered_comments.json")

    # PROMPT FOR PROFILE ANALYSIS
    username = get_profile_username()

    print("\nUsername accepted:" , username)

    # LOAD PROFILE PAGE
    profile_loaded = load_profile_page(driver, username)

    if not profile_loaded:
        print("Profile could not be loaded. Ending program.")
        driver.quit()
        return

    # EXTRACT BASIC PROFILE DATA
    profile_data = extract_basic_profile_data(driver, username)

    # SAVE PROFILE DATA
    save_data_to_json(profile_data, "profile_data.json")

    if profile_data is None:
        print("Failed to extract profile data.")
        driver.quit()
        return

    # PRINT PROFILE DATA
    print("\n--- BASIC PROFILE DATA ---")
    for key, value in profile_data.items():
        print(f"{key}: {value}")

    # OPEN PROFILE DETAILS MENU
    menu_opened = open_profile_details_menu(driver)

    if not menu_opened:
        print("Failed to open profile details menu.")
    else:
        # EXTRACT ABOUT-ACCOUNT DATA
        about_data = extract_about_account_data(driver)

        # SAVE ABOUT ACCOUNT DATA
        save_data_to_json(about_data, "about_account_data.json")

        if about_data is not None:
            print("\n--- ABOUT THIS ACCOUNT DATA ---")
            for key, value in about_data.items():
                print(f"{key}: {value}")

    # COMBINE PROFILE + ABOUT ACCOUNT DATA
    profile_account_data = {
        "profile": profile_data,
        "about_account": about_data
    }

    # SAVE PROFILE + ABOUT ACCOUNT DATA
    save_data_to_json(profile_account_data, "profile_account_data.json")

    # =================================================#

    # BUILD VARIABLE RESULTS
    variable_results = {}

    if about_data is not None:
        variable_results["account_age"] = build_account_age_result(about_data)
        variable_results["username_changed"] = build_username_changes_result(about_data)

    if profile_data is not None:
        variable_results["post_count"] = build_post_count_result(profile_data)
        variable_results["follower_count"] = build_follower_count_result(profile_data)
        variable_results["following_count"] = build_following_count_result(profile_data)
        variable_results["following_follower_ratio"] = build_following_follower_ratio_result(profile_data)

    # CALCULATE SCORES
    total_risk_score = calculate_total_risk_score(variable_results)
    final_score = calculate_final_score(total_risk_score)

    # DISPLAY ONLY FINAL SCORES
    print("\n--- SCORE SUMMARY ---")
    print(f"Risk score: {total_risk_score}")
    print(f"Final score: {final_score}")

    # Browser open temp
    time.sleep(240) # 4 min
    driver.quit() 

if __name__ == "__main__":
    main()