# INSTASENTRY  

# Instagram test link #1: https://www.instagram.com/p/DV6uGIQCdY-/
# Instagram test link #2: https://www.instagram.com/p/DVRbpdJCW7Z/

from user_input import (
    get_post_url, 
    get_comment_limit, 
    get_keywords, 
    confirm_extraction
)
from insta_browser import (
    open_instagram_login,
    load_post_after_login,
    find_comments_container,
    find_comment_candidates,
    scroll_once_for_comments,
    find_scrollable_comment_container,
    scroll_comment_container
)
from comment_processing import (
    extract_top_level_comments,
    print_structured_comments,
    filter_comments_by_keywords,
    print_filtered_comments
)
import time
from config import MAX_COMMENTS, MAX_NO_NEW_SCROLLS
from comment_processing import save_comments_to_file

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

    # Browser open temp
    time.sleep(240) # 4 min
    driver.quit() 

if __name__ == "__main__":
    main()