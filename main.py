# INSTASENTRY  

# Instagram test link #1: https://www.instagram.com/p/DV6uGIQCdY-/
# Instagram test link #2: https://www.instagram.com/p/DVRbpdJCW7Z/

import time
from config import MAX_NO_NEW_SCROLLS
from comment_processing import (
    save_comments_to_file,
    save_data_to_json
)
from user_input import (
    get_post_url,
    get_comment_limit,
    get_keywords,
    confirm_extraction,
    get_profile_username,
    get_analysis_mode # FOR TESTING!!!
)
from insta_browser import (
    open_instagram_login,
    load_post_after_login,
    load_profile_page,
    find_comments_container,
    find_comment_candidates,
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
    build_post_count_result,
    build_follower_count_result,
    build_following_count_result,
    build_following_follower_ratio_result,
    build_private_status_result,
    build_username_structure_result,
    build_name_username_mismatch_result,
    build_links_in_bio_result,
    build_bio_content_result,
    build_hashtags_result,
    build_emoji_usage_result,
    build_propaganda_phrases_result,
    build_emotional_language_result,
    build_country_mentions_result,
    build_comment_length_result,
    build_punctuation_patterns_result,
    build_capitalization_patterns_result,
    build_username_changed_result,
    build_profile_picture_presence_result,
    build_account_location_result,
    build_score_breakdown
)

# MAIN
def main():
    analysis_mode = get_analysis_mode()

    comments = []
    filtered_comments = None
    about_data = None
    post_url = None
    comment_limit = None
    keywords = []

    if analysis_mode == "1":
        # FULL ANALYSIS MODE
        post_url = get_post_url()
        print("\nPost URL accepted:", post_url)

        comment_limit = get_comment_limit()
        print("\nComment limit accepted:", comment_limit)

        keywords = get_keywords()
        print("\nKeywords accepted:")
        print(keywords)

    else:
        # PROFILE-ONLY MODE
        print("\nRunning PROFILE-ONLY analysis...")

    if not confirm_extraction():
        return

    driver = open_instagram_login()

    if driver is None:
        print("Program stopped.")
        return

    # FULL ANALYSIS: COMMENT COLLECTION
    if analysis_mode == "1":
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

    # PROFILE ANALYSIS
    username = get_profile_username()
    print("\nUsername accepted:", username)

    profile_loaded = load_profile_page(driver, username)

    if not profile_loaded:
        print("Profile could not be loaded. Ending program.")
        driver.quit()
        return

    profile_data = extract_basic_profile_data(driver, username)

    if profile_data is None:
        print("Failed to extract profile data.")
        driver.quit()
        return

    save_data_to_json(profile_data, "profile_data.json")

    print("\n--- BASIC PROFILE DATA ---")
    for key, value in profile_data.items():
        print(f"{key}: {value}")

    menu_opened = open_profile_details_menu(driver)

    if not menu_opened:
        print("Failed to open profile details menu.")
    else:
        about_data = extract_about_account_data(driver)

        if about_data is not None:
            save_data_to_json(about_data, "about_account_data.json")

            print("\n--- ABOUT THIS ACCOUNT DATA ---")
            for key, value in about_data.items():
                print(f"{key}: {value}")

    profile_account_data = {
        "profile": profile_data,
        "about_account": about_data
    }

    save_data_to_json(profile_account_data, "profile_account_data.json")

    # BUILD VARIABLE RESULTS
    variable_results = {}

    if about_data is not None:
        variable_results["account_age"] = build_account_age_result(about_data)
        variable_results["username_changed"] = build_username_changed_result(about_data)
        variable_results["account_location"] = build_account_location_result(about_data)

    if profile_data is not None:
        variable_results["post_count"] = build_post_count_result(profile_data)
        variable_results["follower_count"] = build_follower_count_result(profile_data)
        variable_results["following_count"] = build_following_count_result(profile_data)
        variable_results["following_follower_ratio"] = build_following_follower_ratio_result(profile_data)
        variable_results["private_status"] = build_private_status_result(profile_data)
        variable_results["username_structure"] = build_username_structure_result(profile_data)
        variable_results["name_username_mismatch"] = build_name_username_mismatch_result(profile_data)
        variable_results["links_in_bio"] = build_links_in_bio_result(profile_data)
        variable_results["bio_content"] = build_bio_content_result(profile_data)
        variable_results["profile_picture_presence"] = build_profile_picture_presence_result(profile_data)

    if filtered_comments is not None:
        variable_results["hashtags"] = build_hashtags_result(filtered_comments)
        variable_results["emoji_usage"] = build_emoji_usage_result(filtered_comments)
        variable_results["propaganda_phrases"] = build_propaganda_phrases_result(filtered_comments)
        variable_results["emotional_language"] = build_emotional_language_result(filtered_comments)
        variable_results["country_mentions"] = build_country_mentions_result(filtered_comments)
        variable_results["comment_length"] = build_comment_length_result(filtered_comments)
        variable_results["punctuation_patterns"] = build_punctuation_patterns_result(filtered_comments)
        variable_results["capitalization_patterns"] = build_capitalization_patterns_result(filtered_comments)

    # CALCULATE SCORES
    total_risk_score = calculate_total_risk_score(variable_results)
    final_score = calculate_final_score(total_risk_score)

    print("\n--- SCORE SUMMARY ---")
    print(f"Risk score: {total_risk_score}")
    print(f"Final score: {final_score}")

    # BUILD SCORE BREAKDOWN
    score_breakdown = build_score_breakdown(
        variable_results,
        total_risk_score,
        final_score
    )

    # SAVE SCORE BREAKDOWN TO JSON
    save_data_to_json(score_breakdown, "score_breakdown.json")

    time.sleep(240)
    driver.quit()

if __name__ == "__main__":
    main()