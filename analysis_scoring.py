from analysis_compare import (
    compare_account_age,
    compare_username_changes,
    compare_post_count,
    compare_follower_count,
    compare_following_count,
    compare_following_follower_ratio,
    compare_private_status,
    compare_username_structure,
    compare_name_username_mismatch,
    compare_links_in_bio,
    compare_bio_content,
    compare_hashtags,
    compare_emoji_usage,
    compare_propaganda_phrases,
    compare_emotional_language,
    compare_country_mentions,
    compare_comment_length,
    compare_punctuation_patterns,
    compare_capitalization_patterns,
    compare_username_changed,
    compare_profile_picture_presence,
    compare_account_location,
    compare_display_name_presence,
    compare_repetitive_comment_pattern
)
import json
import re

def load_detection_rules():
    try:
        with open("detection_rules.json", "r", encoding="utf-8") as file:
            return json.load(file)
    except Exception:
        return {}

def get_threshold_score(value, threshold_list, default=0):
    try:
        for item in threshold_list:
            max_value = item.get("max")
            if max_value is None or value <= max_value:
                return item.get("score", default)
    except Exception:
        pass
    return default

def get_mapped_score(value, mapping, default=0):
    key = str(value).lower()
    return mapping.get(key, mapping.get(str(value), default))

def check_conditions(data, conditions):
    try:
        for key, value in conditions.items():

            if key.endswith("_max"):
                field = key.replace("_max", "")
                if data.get(field, float("inf")) > value:
                    return False

            elif key.endswith("_min"):
                field = key.replace("_min", "")
                if data.get(field, 0) < value:
                    return False

            elif key == "bio_types":
                if data.get("bio_type") not in value:
                    return False

            elif key == "bio_type":
                if data.get("bio_type") != value:
                    return False

            else:
                if data.get(key) != value:
                    return False

        return True

    except Exception:
        return False


def evaluate_combo_rules(data):
    rules = load_detection_rules()
    combo_rules = rules.get("combo_rules", [])

    triggered_combos = []
    total_combo_score = 0

    for rule in combo_rules:
        conditions = rule.get("conditions", {})
        score = rule.get("score", 0)
        name = rule.get("name", "unnamed_combo")
        reason = rule.get("reason", "A combo rule was triggered.")

        if check_conditions(data, conditions):
            triggered_combos.append({
                "name": name,
                "score": score,
                "reason": reason
            })
            total_combo_score += score

    return {
        "triggered_combos": triggered_combos,
        "total_combo_score": total_combo_score
    }


def get_confidence_label(final_score):
    if 1 <= final_score <= 25:
        return "Very likely automated"
    elif 26 <= final_score <= 50:
        return "Likely automated"
    elif 51 <= final_score <= 70:
        return "Uncertain"
    elif 71 <= final_score <= 85:
        return "Likely human"
    elif 86 <= final_score <= 99:
        return "Highly likely human"
    return "Unknown"


def build_why_report(username, final_score, total_risk_score, variable_results, triggered_combos):
    rules = load_detection_rules()
    max_risk_score = rules.get("max_risk_score", 160)
    confidence = get_confidence_label(final_score)

    lines = []
    lines.append(f"Username: {username}")
    lines.append("")
    lines.append(f"Final Score: {final_score}")
    lines.append(f"Confidence: {confidence}")
    lines.append("")
    lines.append("Reasons:")

    for variable_name, result in variable_results.items():
        score = result.get("score", 0)
        reason = get_variable_reason(variable_name, result)
        lines.append(f"- {reason} ({score})")

    for combo in triggered_combos:
        lines.append(f"- Combo triggered: {combo['reason']} ({combo['score']})")

    lines.append("")
    lines.append(f"Risk Score: {total_risk_score}/{max_risk_score}")

    return "\n".join(lines)

# CONDITION ENGINE
def check_conditions(data, conditions):
    try:
        for key, value in conditions.items():

            if key.endswith("_max"):
                field = key.replace("_max", "")
                if data.get(field, float("inf")) > value:
                    return False

            elif key.endswith("_min"):
                field = key.replace("_min", "")
                if data.get(field, 0) < value:
                    return False

            elif key == "bio_types":
                if data.get("bio_type") not in value:
                    return False

            elif key == "bio_type":
                if data.get("bio_type") != value:
                    return False

            else:
                if data.get(key) != value:
                    return False

        return True

    except Exception:
        return False

# COMBO ENGINE
def calculate_combo_penalty(data):
    rules = load_detection_rules()
    combo_rules = rules.get("combo_rules", [])

    combo_score = 0

    for rule in combo_rules:
        conditions = rule.get("conditions", {})
        score = rule.get("score", 0)

        if check_conditions(data, conditions):
            combo_score += score

    return combo_score

# SCORE ACCOUNT AGE
def score_account_age(account_age_months):
    if account_age_months is None:
        return 0
    rules = load_detection_rules()
    thresholds = rules.get("scoring_thresholds", {}).get("account_age_months", [])
    return get_threshold_score(account_age_months, thresholds)

# BUILD ACCOUNT AGE RESULT
def build_account_age_result(about_data):
    account_age_months = compare_account_age(about_data)
    account_age_score = score_account_age(account_age_months)

    return {
        "raw_value": account_age_months,
        "score": account_age_score
    }

# SCORE USERNAME CHANGES
def score_username_changes(change_count):
    rules = load_detection_rules()
    thresholds = rules.get("scoring_thresholds", {}).get("username_changes", [])
    return get_threshold_score(change_count, thresholds)

# BUILD USERNAME CHANGES RESULT
def build_username_changes_result(about_data):
    change_count = compare_username_changes(about_data)
    score = score_username_changes(change_count)

    return {
        "raw_value": change_count,
        "score": score
    }

# SCORE POST COUNT
def score_post_count(post_count):
    rules = load_detection_rules()
    thresholds = rules.get("scoring_thresholds", {}).get("post_count", [])
    return get_threshold_score(post_count, thresholds)

# BUILD POST COUNT RESULT
def build_post_count_result(profile_data):
    post_count = compare_post_count(profile_data)
    score = score_post_count(post_count)

    return {
        "raw_value": post_count,
        "score": score
    }

# SCORE FOLLOWER COUNT
def score_follower_count(follower_count):
    rules = load_detection_rules()
    thresholds = rules.get("scoring_thresholds", {}).get("follower_count", [])
    return get_threshold_score(follower_count, thresholds)

# BUILD FOLLOWER COUNT RESULT
def build_follower_count_result(profile_data):
    follower_count = compare_follower_count(profile_data)
    score = score_follower_count(follower_count)

    return {
        "raw_value": follower_count,
        "score": score
    }

# SCORE FOLLOWING COUNT
def score_following_count(following_count):
    rules = load_detection_rules()
    thresholds = rules.get("scoring_thresholds", {}).get("following_count", [])
    return get_threshold_score(following_count, thresholds)

# BUILD FOLLOWING COUNT RESULT
def build_following_count_result(profile_data):
    following_count = compare_following_count(profile_data)
    score = score_following_count(following_count)

    return {
        "raw_value": following_count,
        "score": score
    }

# SCORE FOLLOWING / FOLLOWER RATIO
def score_following_follower_ratio(ratio):
    rules = load_detection_rules()
    thresholds = rules.get("scoring_thresholds", {}).get("following_follower_ratio", [])
    return get_threshold_score(ratio, thresholds)

# BUILD FOLLOWING / FOLLOWER RATIO RESULT
def build_following_follower_ratio_result(profile_data):
    ratio = compare_following_follower_ratio(profile_data)
    score = score_following_follower_ratio(ratio)

    return {
        "raw_value": ratio,
        "score": score
    }

# SCORE PRIVATE VS PUBLIC
def score_private_status(is_private):
    rules = load_detection_rules()
    mapping = rules.get("score_maps", {}).get("private_status", {})
    return get_mapped_score(is_private, mapping)

# BUILD PRIVATE STATUS RESULT
def build_private_status_result(profile_data):
    is_private = compare_private_status(profile_data)
    score = score_private_status(is_private)

    return {
        "raw_value": is_private,
        "score": score
    }

# SCORE USERNAME STRUCTURE
def score_username_structure(structure_type):
    rules = load_detection_rules()
    mapping = rules.get("score_maps", {}).get("username_structure", {})
    return get_mapped_score(structure_type, mapping)

# BUILD USERNAME STRUCTURE RESULT
def build_username_structure_result(profile_data):
    structure_type = compare_username_structure(profile_data)
    score = score_username_structure(structure_type)

    return {
        "raw_value": structure_type,
        "score": score
    }

# SCORE NAME / USERNAME MISMATCH
def score_name_username_mismatch(mismatch_type):
    rules = load_detection_rules()
    mapping = rules.get("score_maps", {}).get("name_username_mismatch", {})
    return get_mapped_score(mismatch_type, mapping)

# BUILD NAME / USERNAME MISMATCH RESULT
def build_name_username_mismatch_result(profile_data):
    mismatch_type = compare_name_username_mismatch(profile_data)
    score = score_name_username_mismatch(mismatch_type)

    return {
        "raw_value": mismatch_type,
        "score": score
    }

# SCORE LINKS IN BIO
def score_links_in_bio(match_count):
    rules = load_detection_rules()
    thresholds = rules.get("scoring_thresholds", {}).get("links_in_bio_match_count", [])
    return get_threshold_score(match_count, thresholds)

# BUILD LINKS IN BIO RESULT
def build_links_in_bio_result(profile_data):
    link_result = compare_links_in_bio(profile_data)
    score = score_links_in_bio(link_result["match_count"])

    return {
        "raw_value": link_result,
        "score": score
    }

# HELPER: BIO CONTENT
def match_term(term, text):
    if not term or not text:
        return False

    text = text.lower()
    term = term.lower()

    pattern = r'\b' + re.escape(term) + r'\b'
    return re.search(pattern, text) is not None

# SCORE BIO CONTENT / PATTERN
def score_bio_content(bio_type):
    rules = load_detection_rules()
    mapping = rules.get("score_maps", {}).get("bio_content", {})
    return get_mapped_score(bio_type, mapping)

# BUILD BIO CONTENT RESULT
def build_bio_content_result(profile_data):
    bio_result = compare_bio_content(profile_data)
    score = score_bio_content(bio_result["bio_type"])

    return {
        "raw_value": bio_result,
        "score": score
    }

# ANALYZE BIO CONTENT / PATTERN
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
        bio_rules = rules.get("bio_rules", {})

        vague_length_max = bio_rules.get("vague_length_max", 10)
        emoji_heavy_min = bio_rules.get("emoji_heavy_min", 4)

        matched_terms = []
        emoji_count = sum(1 for char in bio_text if ord(char) > 10000)

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

        if len(bio_text) <= vague_length_max:
            return {
                "bio_type": "vague_minimal",
                "matched_terms": [],
                "emoji_count": emoji_count
            }

        if emoji_count >= emoji_heavy_min:
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

# SCORE DISPLAY NAME PRESENCE
def score_display_name_presence(display_name_present):
    rules = load_detection_rules()
    mapping = rules.get("score_maps", {}).get("display_name_presence", {})
    return get_mapped_score(display_name_present, mapping)

# BUILD DISPLAY NAME PRESENSCE RESULT
def build_display_name_presence_result(profile_data):
    display_name_present = compare_display_name_presence(profile_data)
    score = score_display_name_presence(display_name_present)

    return {
        "raw_value": display_name_present,
        "score": score
    }

# SCORE HASHTAGS
def score_hashtags(total_hashtags):
    rules = load_detection_rules()
    thresholds = rules.get("scoring_thresholds", {}).get("hashtags", [])
    return get_threshold_score(total_hashtags, thresholds)

# BUILD HASHTAGS RESULT
def build_hashtags_result(keyword_comments):
    hashtag_result = compare_hashtags(keyword_comments)
    score = score_hashtags(hashtag_result["total_hashtags"])

    return {
        "raw_value": hashtag_result,
        "score": score
    }

# SCORE EMOJI USAGE
def score_emoji_usage(total_emojis):
    rules = load_detection_rules()
    thresholds = rules.get("scoring_thresholds", {}).get("emoji_usage", [])
    return get_threshold_score(total_emojis, thresholds)

# BUILD EMOJI USAGE RESULT
def build_emoji_usage_result(keyword_comments):
    emoji_result = compare_emoji_usage(keyword_comments)
    score = score_emoji_usage(emoji_result["total_emojis"])

    return {
        "raw_value": emoji_result,
        "score": score
    }

# SCORE PROPAGANDA PHRASES
def score_propaganda_phrases(total_matches):
    rules = load_detection_rules()
    thresholds = rules.get("scoring_thresholds", {}).get("propaganda_phrases", [])
    return get_threshold_score(total_matches, thresholds)

# BUILD PROPAGANDA PHRASES RESULT
def build_propaganda_phrases_result(keyword_comments):
    propaganda_result = compare_propaganda_phrases(keyword_comments)
    score = score_propaganda_phrases(propaganda_result["total_matches"])

    return {
        "raw_value": propaganda_result,
        "score": score
    }

# SCORE EMOTIONAL LANGUAGE
def score_emotional_language(total_matches):
    rules = load_detection_rules()
    thresholds = rules.get("scoring_thresholds", {}).get("emotional_language", [])
    return get_threshold_score(total_matches, thresholds)

# BUILD EMOTIONAL LANGUAGE RESULT
def build_emotional_language_result(filtered_comments):
    emotional_result = compare_emotional_language(filtered_comments)
    score = score_emotional_language(emotional_result["total_matches"])

    return {
        "raw_value": emotional_result,
        "score": score
    }

# SCORE COUNTRY MENTIONS
def score_country_mentions(total_matches):
    rules = load_detection_rules()
    thresholds = rules.get("scoring_thresholds", {}).get("country_mentions", [])
    return get_threshold_score(total_matches, thresholds)

# BUILD COUNTRY MENTIONS RESULT
def build_country_mentions_result(filtered_comments):
    country_result = compare_country_mentions(filtered_comments)
    score = score_country_mentions(country_result["total_matches"])

    return {
        "raw_value": country_result,
        "score": score
    }

# SCORE COMMENT LENGTH
def score_comment_length(avg_length):
    rules = load_detection_rules()
    thresholds = rules.get("scoring_thresholds", {}).get("comment_length_average", [])
    return get_threshold_score(avg_length, thresholds)

# BUILD COMMENT LENGTH RESULT
def build_comment_length_result(filtered_comments):
    length_result = compare_comment_length(filtered_comments)
    score = score_comment_length(length_result["average_length"])

    return {
        "raw_value": length_result,
        "score": score
    }

# SCORE PUNCTUATION PATTERNS
def score_punctuation_patterns(pattern_count):
    rules = load_detection_rules()
    thresholds = rules.get("scoring_thresholds", {}).get("punctuation_patterns", [])
    return get_threshold_score(pattern_count, thresholds)

# BUILD PUNCTUATION PATTERNS RESULT
def build_punctuation_patterns_result(filtered_comments):
    punctuation_result = compare_punctuation_patterns(filtered_comments)
    score = score_punctuation_patterns(punctuation_result["pattern_count"])

    return {
        "raw_value": punctuation_result,
        "score": score
    }

# SCORE CAPITALIZATION PATTERNS
def score_capitalization_patterns(abnormal_count):
    rules = load_detection_rules()
    thresholds = rules.get("scoring_thresholds", {}).get("capitalization_patterns", [])
    return get_threshold_score(abnormal_count, thresholds)

# BUILD CAPITALIZATION RESULT
def build_capitalization_patterns_result(filtered_comments):
    cap_result = compare_capitalization_patterns(filtered_comments)
    score = score_capitalization_patterns(cap_result["abnormal_count"])

    return {
        "raw_value": cap_result,
        "score": score
    }

# SCORE REPETITIVE COMMENT PATTERN
def score_repetitive_comment_pattern(pattern_type):
    rules = load_detection_rules()
    mapping = rules.get("score_maps", {}).get("repetitive_comment_pattern", {})
    return get_mapped_score(pattern_type, mapping)

# BUILD REPETITIVE COMMENT PATTERN
def build_repetitive_comment_pattern_result(filtered_comments):
    pattern_result = compare_repetitive_comment_pattern(filtered_comments)
    score = score_repetitive_comment_pattern(pattern_result["pattern_type"])

    return {
        "raw_value": pattern_result,
        "score": score
    }

# SCORE USERNAME CHANGED
def score_username_changed(change_count, account_age_months):
    if account_age_months is None:
        return 0

    years = max(account_age_months / 12, 0.5)
    change_rate = change_count / years

    rules = load_detection_rules()
    thresholds = rules.get("scoring_thresholds", {}).get("username_changed_rate", [])
    return get_threshold_score(change_rate, thresholds)

# BUILD USERNAME CHANGED RESULT
def build_username_changed_result(about_data):
    change_count = compare_username_changed(about_data)
    account_age_months = compare_account_age(about_data)
    score = score_username_changed(change_count, account_age_months)

    return {
        "raw_value": {
            "changes": change_count,
            "account_age_months": account_age_months
        },
        "score": score
    }

# SCORE PROFILE PICTURE PRESENCE
def score_profile_picture_presence(profile_picture_present):
    rules = load_detection_rules()
    mapping = rules.get("score_maps", {}).get("profile_picture_presence", {})
    return get_mapped_score(profile_picture_present, mapping)

# BUILD PROFILE PICTURE PRESENCE RESULT
def build_profile_picture_presence_result(profile_data):
    profile_picture_present = compare_profile_picture_presence(profile_data)
    score = score_profile_picture_presence(profile_picture_present)

    return {
        "raw_value": profile_picture_present,
        "score": score
    }

# SCORE ACCOUNT LOCATION
def score_account_location(location_type):
    rules = load_detection_rules()
    mapping = rules.get("score_maps", {}).get("account_location", {})
    return get_mapped_score(location_type, mapping)

# BUILD ACCOUNT LOCATION RESULT
def build_account_location_result(about_data):
    location_type = compare_account_location(about_data)
    score = score_account_location(location_type)

    return {
        "raw_value": location_type,
        "score": score
    }

# =================================================#

# HELPER: BUILD RANGE-BASED REASON FROM JSON THRESHOLDS
def build_range_reason(value, thresholds, label):
    try:
        if value is None:
            return f"{label} could not be determined."

        for i, item in enumerate(thresholds):
            max_val = item.get("max")

            if max_val is None or value <= max_val:
                if i == 0:
                    return f"{label} is {value}."

                prev_max = thresholds[i - 1].get("max")
                lower = (prev_max + 1) if prev_max is not None else 0

                if max_val is None:
                    return f"{label} is {lower} or more."
                elif lower == max_val:
                    return f"{label} is {lower}."
                else:
                    return f"{label} is between {lower} and {max_val}."

        return f"{label} is {value}."

    except Exception:
        return f"{label} could not be interpreted."


# BUILD HUMAN-READABLE REASON FOR EACH VARIABLE
def get_variable_reason(variable_name, result):
    raw_value = result.get("raw_value")
    score = result.get("score")

    rules = load_detection_rules()
    thresholds = rules.get("scoring_thresholds", {})

    if variable_name == "account_age":
        if raw_value is None:
            return "Account age could not be determined."
        elif raw_value >= 84:
            return "Account is 7 or more years old."
        elif raw_value >= 60:
            return "Account is between 5 and less than 7 years old."
        elif raw_value >= 36:
            return "Account is between 3 and less than 5 years old."
        elif raw_value >= 12:
            return "Account is between 1 and less than 3 years old."
        else:
            return "Account is less than 1 year old."

    elif variable_name == "username_changed":
        changes = raw_value.get("changes", 0)
        age_months = raw_value.get("account_age_months")

        if age_months is None:
            return "Username change count found, but account age could not be determined."

        years = max(age_months / 12, 0.5)
        change_rate = changes / years

        return f"{changes} username change(s) detected over about {years:.1f} year(s). Rate: {change_rate:.2f} per year."

    elif variable_name == "account_location":
        if raw_value == "normal":
            return "Account-based location is normal or low-risk."
        elif raw_value == "unknown":
            return "Account-based location could not be confirmed."
        else:
            return "Account-based location matches a high-risk country."

    elif variable_name == "post_count":
        return build_range_reason(raw_value, thresholds.get("post_count", []), "Account post count")

    elif variable_name == "follower_count":
        return build_range_reason(raw_value, thresholds.get("follower_count", []), "Follower count")

    elif variable_name == "following_count":
        return build_range_reason(raw_value, thresholds.get("following_count", []), "Following count")

    elif variable_name == "following_follower_ratio":
        if raw_value == float("inf"):
            return "Account follows others but has 0 followers."
        return build_range_reason(raw_value, thresholds.get("following_follower_ratio", []), "Following/follower ratio")

    elif variable_name == "private_status":
        return "Account is private." if raw_value else "Account is public."

    elif variable_name == "username_structure":
        mapping = {
            "normal": "Username appears normal and readable.",
            "generic_handle": "Username appears generic and ends with numbers.",
            "minor_numbers_symbols": "Username contains minor numbers or symbols.",
            "random_pattern": "Username contains a structured numeric pattern.",
            "highly_random": "Username appears highly random or automated."
        }
        return mapping.get(raw_value, "Username structure could not be determined.")

    elif variable_name == "display_name_presence":
        return "Display name is present." if raw_value else "Display name is missing."

    elif variable_name == "name_username_mismatch":
        mapping = {
            "consistent": "Display name and username are consistent.",
            "no_display_name": "Display name is missing, so comparison was not performed.",
            "minor_variation": "Display name and username are similar with minor variation.",
            "noticeable_mismatch": "Display name and username show a noticeable mismatch.",
            "completely_inconsistent": "Display name and username appear completely inconsistent."
        }
        return mapping.get(raw_value, "Name/username comparison could not be determined.")

    elif variable_name == "links_in_bio":
        match_count = raw_value.get("match_count", 0)
        matched_terms = raw_value.get("matched_terms", [])
        if match_count == 0:
            return "No flagged link terms detected in bio links."
        return f"Flagged bio link terms detected: {', '.join(matched_terms)}."

    elif variable_name == "bio_content":
        bio_type = raw_value.get("bio_type", "normal")
        mapping = {
            "normal": "Bio appears normal.",
            "vague_minimal": "Bio appears vague or minimal.",
            "generic_or_emoji_heavy": "Bio appears generic or emoji-heavy.",
            "propaganda_or_coordinated": "Bio contains coordinated or suspicious messaging.",
            "no_bio": "Bio is empty."
        }
        return mapping.get(bio_type, "Bio could not be analyzed.")

    elif variable_name == "profile_picture_presence":
        return "Profile picture is present." if raw_value else "Profile picture is missing or could not be confirmed."

    elif variable_name == "hashtags":
        return f"{raw_value.get('total_hashtags', 0)} hashtag(s) detected in filtered comments."

    elif variable_name == "emoji_usage":
        return f"{raw_value.get('total_emojis', 0)} emoji(s) detected in filtered comments."

    elif variable_name == "propaganda_phrases":
        total = raw_value.get("total_matches", 0)
        matched = raw_value.get("matched_phrases", [])
        return "No propaganda phrases detected." if total == 0 else f"{total} propaganda phrase match(es): {', '.join(matched)}."

    elif variable_name == "emotional_language":
        total = raw_value.get("total_matches", 0)
        matched = raw_value.get("matched_words", [])
        return "No emotional language detected." if total == 0 else f"{total} emotional word match(es): {', '.join(matched)}."

    elif variable_name == "country_mentions":
        total = raw_value.get("total_matches", 0)
        matched = raw_value.get("matched_terms", [])
        return "No country mentions detected." if total == 0 else f"{total} country mention(s): {', '.join(matched)}."

    elif variable_name == "comment_length":
        return f"Average filtered comment length is {raw_value.get('average_length', 0):.2f} characters."

    elif variable_name == "punctuation_patterns":
        count = raw_value.get("pattern_count", 0)
        return "No repeated punctuation patterns detected." if count == 0 else f"{count} repeated punctuation pattern(s) detected."

    elif variable_name == "capitalization_patterns":
        count = raw_value.get("abnormal_count", 0)
        return "No abnormal capitalization patterns detected." if count == 0 else f"{count} abnormal capitalization pattern(s) detected."

    elif variable_name == "repetitive_comment_pattern":
        pattern_type = raw_value.get("pattern_type", "none")
        repeated_phrases = raw_value.get("repeated_phrases", [])
        long_comment_count = raw_value.get("long_comment_count", 0)

        if pattern_type == "none":
            return "No repetitive or spam-like behavior detected."
        elif pattern_type == "mild":
            return f"Mild repetition detected. Long comments: {long_comment_count}."
        elif pattern_type == "heavy":
            return f"Heavy repetitive behavior detected. Long comments: {long_comment_count}."
        else:
            return f"Extreme repetition detected. Examples: {', '.join(repeated_phrases)}."

    return f"Variable scored {score} point(s)."

# BUILD FULL SCORE BREAKDOWN
def build_score_breakdown(variable_results, total_risk_score, final_score):
    breakdown_variables = {}

    for variable_name, result in variable_results.items():
        breakdown_variables[variable_name] = {
            "raw_value": result.get("raw_value"),
            "score": result.get("score"),
            "reason": get_variable_reason(variable_name, result)
        }

    return {
        "variables": breakdown_variables,
        "risk_score": total_risk_score,
        "final_score": final_score
    }

# =================================================#

# CALCULATE TOTAL RISK SCORE
def calculate_total_risk_score(variable_results, combo_data=None):
    total_risk_score = 0

    for result in variable_results.values():
        total_risk_score += result["score"]

    if combo_data is not None:
        combo_result = evaluate_combo_rules(combo_data)
        total_risk_score += combo_result["total_combo_score"]

    return total_risk_score

# CALCULATE FINAL 0-99 SCORE
def calculate_final_score(total_risk_score, max_risk_score=160):    # Subject to change
    final_score = 99 - round((total_risk_score / max_risk_score) * 98)

    if final_score < 1:
        final_score = 1
    elif final_score > 99:
        final_score = 99

    return final_score

