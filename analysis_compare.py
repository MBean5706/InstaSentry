from datetime import datetime
import re
import json

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
        return 0

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

# GET PRIVATE / PUBLIC STATUS
def compare_private_status(profile_data):
    try:
        return profile_data.get("is_private", False)
    except Exception:
        return False

# ANALYZE USERNAME STRUCTURE
def compare_username_structure(profile_data):
    try:
        username = profile_data.get("username", "")

        if username is None:
            return "normal"

        username = str(username).strip().lower()

        digit_count = sum(char.isdigit() for char in username)
        underscore_count = username.count("_")
        period_count = username.count(".")
        symbol_count = underscore_count + period_count

        # highly random / many digits
        if digit_count >= 6:
            return "highly_random"

        # long numeric sequence or random pattern
        if re.search(r"\d{4,}", username):
            return "random_pattern"

        # minor numbers or symbols
        if digit_count > 0 or symbol_count > 0:
            return "minor_numbers_symbols"

        # normal readable username
        return "normal"

    except Exception:
        return "normal"
    
# ANALYZE DISPLAY NAME VS USERNAME MISMATCH
def compare_name_username_mismatch(profile_data):
    try:
        display_name = profile_data.get("display_name", "")
        username = profile_data.get("username", "")

        if display_name is None or username is None:
            return "consistent"

        display_name_clean = str(display_name).lower().strip().replace(" ", "")
        username_clean = str(username).lower().strip().replace("_", "").replace(".", "")

        # exact / very close match
        if display_name_clean == username_clean:
            return "consistent"

        if display_name_clean in username_clean or username_clean in display_name_clean:
            return "minor_variation"

        # split display name into parts
        name_parts = str(display_name).lower().strip().split()

        # if any major part of display name appears in username
        for part in name_parts:
            if len(part) >= 3 and part in username_clean:
                return "minor_variation"

        # partial weak overlap
        overlap_count = 0
        for char in set(display_name_clean):
            if char in username_clean and char.isalpha():
                overlap_count += 1

        if overlap_count >= 4:
            return "noticeable_mismatch"

        return "completely_inconsistent"

    except Exception:
        return "consistent"

# LOAD DETECTION RULES
def load_detection_rules():
    try:
        with open("detection_rules.json", "r", encoding="utf-8") as file:
            return json.load(file)
    except Exception:
        return {}

# ANALYZE LINKS IN BIO
def compare_links_in_bio(profile_data):
    try:
        links = profile_data.get("links")
        rules = load_detection_rules()
        flagged_terms = rules.get("flagged_link_terms", [])

        if links is None:
            return {
                "match_count": 0,
                "matched_terms": []
            }

        match_count = 0
        matched_terms = []

        for link in links:
            link_lower = str(link).lower()

            for term in flagged_terms:
                if term.lower() in link_lower:
                    match_count += 1
                    matched_terms.append(term)

        return {
            "match_count": match_count,
            "matched_terms": matched_terms
        }

    except Exception:
        return {
            "match_count": 0,
            "matched_terms": []
        }

# ANALYZE BIO CONTENT / PATTERN
def compare_bio_content(profile_data):
    try:
        bio = profile_data.get("bio")

        if bio is None:
            return {
                "bio_type": "vague_minimal",
                "matched_terms": [],
                "emoji_count": 0
            }

        bio_text = str(bio).strip()
        bio_lower = bio_text.lower()

        rules = load_detection_rules()
        flagged_bio_terms = rules.get("flagged_bio_terms", [])
        vague_bio_terms = rules.get("vague_bio_terms", [])

        matched_terms = []
        emoji_count = sum(1 for char in bio_text if ord(char) > 10000)

        for term in flagged_bio_terms:
            if term.lower() in bio_lower:
                matched_terms.append(term)

        if len(matched_terms) > 0:
            return {
                "bio_type": "propaganda_or_coordinated",
                "matched_terms": matched_terms,
                "emoji_count": emoji_count
            }

        for term in vague_bio_terms:
            if term.lower() in bio_lower:
                return {
                    "bio_type": "vague_minimal",
                    "matched_terms": [term],
                    "emoji_count": emoji_count
                }

        if len(bio_text) <= 10:
            return {
                "bio_type": "vague_minimal",
                "matched_terms": [],
                "emoji_count": emoji_count
            }

        if emoji_count >= 4:
            return {
                "bio_type": "generic_or_emoji_heavy",
                "matched_terms": [],
                "emoji_count": emoji_count
            }

        return {
            "bio_type": "normal",
            "matched_terms": [],
            "emoji_count": emoji_count
        }

    except Exception:
        return {
            "bio_type": "normal",
            "matched_terms": [],
            "emoji_count": 0
        }

# ANALYZE HASHTAGS IN COMMENTS
def compare_hashtags(keyword_comments):
    try:
        total_hashtags = 0

        for comment in keyword_comments:
            text = str(comment.get("text", ""))
            hashtags = re.findall(r"#\w+", text)
            total_hashtags += len(hashtags)

        return {
            "total_hashtags": total_hashtags
        }

    except Exception:
        return {
            "total_hashtags": 0
        }

# ANALYZE EMOJI USAGE IN COMMENTS
def compare_emoji_usage(keyword_comments):
    try:
        total_emojis = 0

        for comment in keyword_comments:
            text = str(comment.get("text", ""))

            # Emoji detection via unicode range
            emojis = [char for char in text if ord(char) > 10000]
            total_emojis += len(emojis)

        return {
            "total_emojis": total_emojis
        }

    except Exception:
        return {
            "total_emojis": 0
        }

# ANALYZE PROPAGANDA PHRASES IN COMMENTS
def compare_propaganda_phrases(keyword_comments):
    try:
        rules = load_detection_rules()
        propaganda_phrases = rules.get("propaganda_phrases", [])

        total_matches = 0
        matched_phrases = []

        for comment in keyword_comments:
            text = str(comment.get("text", "")).lower()

            for phrase in propaganda_phrases:
                if phrase.lower() in text:
                    total_matches += 1
                    matched_phrases.append(phrase)

        return {
            "total_matches": total_matches,
            "matched_phrases": matched_phrases
        }

    except Exception:
        return {
            "total_matches": 0,
            "matched_phrases": []
        }

# ANALYZE EMOTIONAL LANGUAGE IN COMMENTS
def compare_emotional_language(filtered_comments):
    try:
        rules = load_detection_rules()
        emotional_words = rules.get("emotional_words", [])

        total_matches = 0
        matched_words = []

        for comment in filtered_comments:
            text = str(comment.get("text", "")).lower()

            for word in emotional_words:
                if word in text:
                    total_matches += 1
                    matched_words.append(word)

        return {
            "total_matches": total_matches,
            "matched_words": matched_words
        }

    except Exception:
        return {
            "total_matches": 0,
            "matched_words": []
        }

# ANALYZE COUNTRY MENTIONS IN COMMENTS
def compare_country_mentions(filtered_comments):
    try:
        rules = load_detection_rules()
        country_terms = rules.get("country_terms", [])

        total_matches = 0
        matched_terms = []

        for comment in filtered_comments:
            text = str(comment.get("text", "")).lower()

            for term in country_terms:
                if term.lower() in text:
                    total_matches += 1
                    matched_terms.append(term)

        return {
            "total_matches": total_matches,
            "matched_terms": matched_terms
        }

    except Exception:
        return {
            "total_matches": 0,
            "matched_terms": []
        }

# ANALYZE COMMENT LENGTH
def compare_comment_length(filtered_comments):
    try:
        if not filtered_comments:
            return {
                "average_length": 0
            }

        total_length = 0
        count = 0

        for comment in filtered_comments:
            text = str(comment.get("text", ""))
            total_length += len(text)
            count += 1

        average_length = total_length / count if count > 0 else 0

        return {
            "average_length": average_length
        }

    except Exception:
        return {
            "average_length": 0
        }

import re

# ANALYZE PUNCTUATION PATTERNS
def compare_punctuation_patterns(filtered_comments):
    try:
        pattern_count = 0

        for comment in filtered_comments:
            text = str(comment.get("text", ""))

            # detect repeated punctuation like !!! or ???
            matches = re.findall(r"[!?]{2,}", text)
            pattern_count += len(matches)

        return {
            "pattern_count": pattern_count
        }

    except Exception:
        return {
            "pattern_count": 0
        }

# ANALYZE CAPITALIZATION PATTERNS
def compare_capitalization_patterns(filtered_comments):
    try:
        abnormal_count = 0

        for comment in filtered_comments:
            text = str(comment.get("text", ""))

            if not text:
                continue

            letters = [c for c in text if c.isalpha()]

            if len(letters) == 0:
                continue

            upper_count = sum(1 for c in letters if c.isupper())
            ratio = upper_count / len(letters)

            # ALL CAPS or near ALL CAPS
            if ratio > 0.7:
                abnormal_count += 1
                continue

            # weird alternating caps
            if any(
                text[i].islower() and text[i+1].isupper()
                for i in range(len(text)-1)
            ):
                abnormal_count += 1

        return {
            "abnormal_count": abnormal_count
        }

    except Exception:
        return {
            "abnormal_count": 0
        }

# GET FORMER USERNAME CHANGE COUNT
def compare_username_changed(about_data):
    try:
        value = about_data.get("former_usernames")

        if value is None:
            return 0

        value = str(value).strip()

        digits = "".join(char for char in value if char.isdigit())

        if digits == "":
            return 0

        return int(digits)

    except Exception:
        return 0

# GET PROFILE PICTURE PRESENCE
def compare_profile_picture_presence(profile_data):
    try:
        return profile_data.get("profile_picture_present", False)
    except Exception:
        return False
    
# ANALYZE ACCOUNT-BASED LOCATION
def compare_account_location(about_data):
    try:
        location = about_data.get("account_based_in")

        if location is None:
            return "unknown"

        location_clean = str(location).lower().strip()

        rules = load_detection_rules()
        high_risk = rules.get("high_risk_countries", [])

        for country in high_risk:
            if country in location_clean:
                return "high_risk"

        return "normal"

    except Exception:
        return "unknown"
    
