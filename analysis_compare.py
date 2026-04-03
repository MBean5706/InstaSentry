from datetime import datetime

# CONVERT "MONTH YEAR" TO ACCOUNT AGE IN MONTHS
def calculate_account_age_in_months(date_joined_str):
    try:
        join_date = datetime.strptime(date_joined_str, "%B %Y")
        now = datetime.now()

        months = (now.year - join_date.year) * 12 + (now.month - join_date.month)

        return months

    except Exception:
        return None

# GET ACCOUNT AGE IN MONTHS FROM ABOUT-ACCOUNT DATA
def compare_account_age(about_data):
    try:
        date_joined = about_data.get("date_joined")

        if date_joined is None:
            return None

        account_age_months = calculate_account_age_in_months(date_joined)
        return account_age_months

    except Exception:
        return None

# GET NUMBER OF USERNAME CHANGES
def compare_username_changes(about_data):
    try:
        value = about_data.get("former_usernames")

        if value is None:
            return 0

        # Extract number if it's in string form
        # Example: "3 former usernames"
        number = int(''.join(filter(str.isdigit, str(value))))

        return number

    except Exception:
        return 0

# GET POST COUNT
def compare_post_count(profile_data):
    try:
        value = profile_data.get("posts")

        if value is None:
            return 0

        number = int(''.join(filter(str.isdigit, str(value))))

        return number

    except Exception:
        return 0

# GET FOLLOWER COUNT
def compare_follower_count(profile_data):
    try:
        value = profile_data.get("followers")

        if value is None:
            return 0

        value = str(value).lower().replace(",", "").strip()

        if "k" in value:
            return int(float(value.replace("k", "")) * 1000)
        elif "m" in value:
            return int(float(value.replace("m", "")) * 1000000)
        else:
            number = int(''.join(filter(str.isdigit, value)))
            return number

    except Exception:
        return

# GET FOLLOWING COUNT
def compare_following_count(profile_data):
    try:
        value = profile_data.get("following")

        if value is None:
            return 0

        value = str(value).lower().replace(",", "").strip()

        if "k" in value:
            return int(float(value.replace("k", "")) * 1000)
        elif "m" in value:
            return int(float(value.replace("m", "")) * 1000000)
        else:
            number = int(''.join(filter(str.isdigit, value)))
            return number

    except Exception:
        return 0

# GET FOLLOWING / FOLLOWER RATIO
def compare_following_follower_ratio(profile_data):
    try:
        follower_count = compare_follower_count(profile_data)
        following_count = compare_following_count(profile_data)

        if follower_count == 0:
            if following_count == 0:
                return 0
            return float("inf")

        ratio = following_count / follower_count
        return ratio

    except Exception:
        return 0