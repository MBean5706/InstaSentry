from config import MAX_COMMENTS, MAX_NO_NEW_SCROLLS

# FOR TESTING!!!
def get_analysis_mode():
    while True:
        mode = input("\nSelect analysis mode: 1 = Full Analysis, 2 = Profile Only: ").strip()

        if mode in ["1", "2"]:
            return mode

        print("Invalid input. Please enter 1 or 2.")

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

# COMMENT COUNT SELECTION
def get_comment_limit():
    while True:
        comment_limit = input(f"\nHow many comments would you like to collect? (max {MAX_COMMENTS}): ").strip()

        if comment_limit == "":
            print("Error: Comment limit cannot be empty. Please try again.")
            continue

        if not comment_limit.isdigit():
            print(f"Error: Please enter a whole number between 1 and {MAX_COMMENTS}.")
            continue

        comment_limit = int(comment_limit)

        if comment_limit < 1 or comment_limit > MAX_COMMENTS:
            print(f"Error: Comment limit must be between 1 and {MAX_COMMENTS}.")
            continue

        return comment_limit

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
        choice = input("\nContinue? (Y/N): ").strip().lower()

        if choice == "y":
            print("\nLoading login window...")
            return True

        elif choice == "n":
            print("\nExtraction canceled.")
            return False

        else:
            print("Invalid input. Please enter Y or N.")

# USERNAME SUBMISSION FOR PROFILE ANALYSIS
def get_profile_username():
    while True:
        username = input("\nEnter the Instagram username to analyze: ").strip()

        if username == "":
            print("Username cannot be empty. Please try again.")
            continue

        if "@" in username:
            username = username.replace("@", "").strip()

        if " " in username:
            print("Username cannot contain spaces. Please try again.")
            continue

        return username