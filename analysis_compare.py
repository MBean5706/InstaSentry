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

        # long numeric sequence
        if re.search(r"\d{4,}", username):
            return "random_pattern"

        # readable name + small number ending like drew22511 / mike2024
        if re.match(r"^[a-z]+[0-9]{2,5}$", username):
            return "generic_handle"

        # readable username with minor symbols or small numbers
        if digit_count > 0 or symbol_count > 0:
            return "minor_numbers_symbols"

        return "normal"

    except Exception:
        return "normal"

# CHECK IF DISPLAY NAME IS PRESENT
def compare_display_name_presence(profile_data):
    try:
        display_name = profile_data.get("display_name")

        if display_name is None:
            return False

        if str(display_name).strip() == "":
            return False

        return True

    except Exception:
        return False

# ANALYZE DISPLAY NAME VS USERNAME MISMATCH
def compare_name_username_mismatch(profile_data):
    try:
        display_name = profile_data.get("display_name")
        username = profile_data.get("username")

        # ✅ OPTION A: if no display name → cannot compare
        if display_name is None or str(display_name).strip() == "":
            return "no_display_name"

        if username is None or str(username).strip() == "":
            return "consistent"

        display_name_clean = str(display_name).lower().strip()
        username_clean = str(username).lower().strip()

        username_clean = username_clean.replace("_", "").replace(".", "")

        name_parts = [part for part in display_name_clean.split() if len(part) >= 3]

        # strong match
        for part in name_parts:
            if part in username_clean:
                return "consistent"

        # partial match
        for part in name_parts:
            if len(part) >= 4 and part[:3] in username_clean:
                return "minor_variation"

        return "completely_inconsistent"

    except Exception:
        return "no_display_name"

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
def match_term(term, text):
    if not term or not text:
        return False

    text = text.lower()
    term = term.lower()

    pattern = r'\b' + re.escape(term) + r'\b'
    return re.search(pattern, text) is not None

def compare_bio_content(profile_data):
    try:
        bio = profile_data.get("bio")

        if bio is None or str(bio).strip() == "":
            return {
                "bio_type": "no_bio",
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

        #MATCHING (NO PARTIAL MATCHES)
        for term in flagged_bio_terms:
            if match_term(term, bio_lower):
                matched_terms.append(term)

        if len(matched_terms) > 0:
            return {
                "bio_type": "propaganda_or_coordinated",
                "matched_terms": list(set(matched_terms)),
                "emoji_count": emoji_count
            }

        for term in vague_bio_terms:
            if match_term(term, bio_lower):
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

# ANALYZE REPETITIVE COMMENT PATTERNS    
def compare_repetitive_comment_pattern(filtered_comments):
    try:
        if not filtered_comments:
            return {
                "pattern_type": "none",
                "repeated_phrases": [],
                "long_comment_count": 0
            }

        repeated_phrases = []
        long_comment_count = 0
        total_repetition_hits = 0

        for comment in filtered_comments:
            text = str(comment.get("text", "")).lower().strip()

            if len(text) >= 180:
                long_comment_count += 1

            # split into rough phrase chunks
            parts = [part.strip() for part in re.split(r"[.!?]", text) if part.strip() != ""]

            seen_parts = {}
            for part in parts:
                if len(part) >= 15:
                    seen_parts[part] = seen_parts.get(part, 0) + 1

            for part, count in seen_parts.items():
                if count >= 2:
                    total_repetition_hits += 1
                    repeated_phrases.append(part)

            # repeated word pattern like "iran iran iran" or spam stacking
            words = re.findall(r"\b\w+\b", text)
            if len(words) >= 8:
                unique_ratio = len(set(words)) / len(words)
                if unique_ratio < 0.55:
                    total_repetition_hits += 1

        if total_repetition_hits == 0 and long_comment_count == 0:
            pattern_type = "none"
        elif total_repetition_hits <= 1 and long_comment_count <= 1:
            pattern_type = "mild"
        elif total_repetition_hits <= 3 or long_comment_count >= 1:
            pattern_type = "heavy"
        else:
            pattern_type = "extreme"

        return {
            "pattern_type": pattern_type,
            "repeated_phrases": repeated_phrases[:5],
            "long_comment_count": long_comment_count
        }

    except Exception:
        return {
            "pattern_type": "none",
            "repeated_phrases": [],
            "long_comment_count": 0
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
