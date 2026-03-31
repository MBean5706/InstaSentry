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
        comment_limit = input("\nHow many comments would you like to collect? (max 100): ").strip()

        if comment_limit == "":
            print("Comment limit cannot be empty. Please try again.")
            continue

        if not comment_limit.isdigit():
            print("Please enter a whole number between 1 and 100.")
            continue

        comment_limit = int(comment_limit)

        if comment_limit < 1 or comment_limit > 100:
            print("Comment limit must be between 1 and 100.")
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
        choice = input("\nReady to extract comments? (Y/N): ").strip().lower()

        if choice == "y":
            print("\nLoading login window...")
            return True

        elif choice == "n":
            print("\nExtraction canceled.")
            return False

        else:
            print("Invalid input. Please enter Y or N.")