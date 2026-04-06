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
    compare_account_location
)

# SCORE ACCOUNT AGE
def score_account_age(account_age_months):
    if account_age_months is None:
        return 0

    if account_age_months > 12:
        return 0
    elif 6 <= account_age_months <= 12:
        return 2
    elif 2 <= account_age_months <= 5:
        return 4
    else:
        return 7

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
    if change_count == 0:
        return 0
    elif 1 <= change_count <= 2:
        return 2
    elif 3 <= change_count <= 5:
        return 4
    else:
        return 6

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
    if post_count >= 10:
        return 0
    elif 5 <= post_count <= 9:
        return 2
    elif 1 <= post_count <= 4:
        return 4
    else:
        return 6

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
    if follower_count >= 100:
        return 0
    elif 10 <= follower_count <= 99:
        return 1
    else:
        return 2

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
    if following_count <= 100:
        return 0
    elif 101 <= following_count <= 500:
        return 1
    else:
        return 2

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
    if ratio <= 1:
        return 0
    elif ratio <= 3:
        return 1
    elif ratio <= 10:
        return 2
    else:
        return 3
    
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
    if is_private:
        return 0
    else:
        return 1

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
    if structure_type == "normal":
        return 0
    elif structure_type == "minor_numbers_symbols":
        return 1
    elif structure_type == "random_pattern":
        return 2
    else:
        return 3
    
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
    if mismatch_type == "consistent":
        return 0
    elif mismatch_type == "minor_variation":
        return 2
    elif mismatch_type == "noticeable_mismatch":
        return 4
    else:
        return 6
    
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
    if match_count == 0:
        return 0
    elif match_count == 1:
        return 2
    elif match_count == 2:
        return 4
    else:
        return 6
    
# BUILD LINKS IN BIO RESULT
def build_links_in_bio_result(profile_data):
    link_result = compare_links_in_bio(profile_data)
    score = score_links_in_bio(link_result["match_count"])

    return {
        "raw_value": link_result,
        "score": score
    }

# SCORE BIO CONTENT / PATTERN
def score_bio_content(bio_type):
    if bio_type == "normal":
        return 0
    elif bio_type == "vague_minimal":
        return 2
    elif bio_type == "generic_or_emoji_heavy":
        return 4
    else:
        return 6

# BUILD BIO CONTENT RESULT
def build_bio_content_result(profile_data):
    bio_result = compare_bio_content(profile_data)
    score = score_bio_content(bio_result["bio_type"])

    return {
        "raw_value": bio_result,
        "score": score
    }

# SCORE HASHTAGS
def score_hashtags(total_hashtags):
    if total_hashtags == 0:
        return 0
    elif total_hashtags <= 2:
        return 1
    elif total_hashtags <= 5:
        return 2
    else:
        return 3

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
    if total_emojis == 0:
        return 0
    elif total_emojis <= 3:
        return 1
    elif total_emojis <= 7:
        return 2
    else:
        return 3

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
    if total_matches == 0:
        return 0
    elif total_matches == 1:
        return 2
    elif 2 <= total_matches <= 3:
        return 4
    else:
        return 6
    
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
    if total_matches == 0:
        return 0
    elif total_matches == 1:
        return 2
    elif 2 <= total_matches <= 3:
        return 4
    else:
        return 6

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
    if total_matches == 0:
        return 0
    elif total_matches == 1:
        return 1
    elif 2 <= total_matches <= 3:
        return 2
    else:
        return 3

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
    if avg_length >= 10:
        return 0
    else:
        return 1

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
    if pattern_count == 0:
        return 0
    else:
        return 1
    
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
    if abnormal_count == 0:
        return 0
    else:
        return 1
    
# BUILD CAPITALIZATION RESULT
def build_capitalization_patterns_result(filtered_comments):
    cap_result = compare_capitalization_patterns(filtered_comments)
    score = score_capitalization_patterns(cap_result["abnormal_count"])

    return {
        "raw_value": cap_result,
        "score": score
    }

# SCORE USERNAME CHANGED
def score_username_changed(change_count):
    if change_count == 0:
        return 0
    elif 1 <= change_count <= 2:
        return 2
    elif 3 <= change_count <= 5:
        return 4
    else:
        return 6
    
# BUILD USERNAME CHANGED RESULT
def build_username_changed_result(about_data):
    change_count = compare_username_changed(about_data)
    score = score_username_changed(change_count)

    return {
        "raw_value": change_count,
        "score": score
    }

# SCORE PROFILE PICTURE PRESENCE
def score_profile_picture_presence(profile_picture_present):
    if profile_picture_present:
        return 0
    else:
        return 2
    
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
    if location_type == "normal":
        return 0
    elif location_type == "unknown":
        return 2
    elif location_type == "high_risk":
        return 4
    else:
        return 0

# BUILD ACCOUNT LOCATION RESULT
def build_account_location_result(about_data):
    location_type = compare_account_location(about_data)
    score = score_account_location(location_type)

    return {
        "raw_value": location_type,
        "score": score
    }

# =================================================#

# BUILD HUMAN-READABLE REASON FOR EACH VARIABLE
def get_variable_reason(variable_name, result):
    raw_value = result.get("raw_value")
    score = result.get("score")

    if variable_name == "account_age":
        if raw_value is None:
            return "Account age could not be determined."
        elif raw_value > 12:
            return "Account older than 12 months."
        elif 6 <= raw_value <= 12:
            return "Account age is between 6 and 12 months."
        elif 2 <= raw_value <= 5:
            return "Account age is between 2 and 5 months."
        else:
            return "Account age is between 0 and 1 month."

    elif variable_name == "username_changed":
        if raw_value == 0:
            return "No username changes detected."
        elif 1 <= raw_value <= 2:
            return "1 to 2 username changes detected."
        elif 3 <= raw_value <= 5:
            return "3 to 5 username changes detected."
        else:
            return "6 or more username changes detected."

    elif variable_name == "account_location":
        if raw_value == "normal":
            return "Account-based location is normal or low-risk."
        elif raw_value == "unknown":
            return "Account-based location could not be confirmed."
        else:
            return "Account-based location matches a high-risk country."

    elif variable_name == "post_count":
        if raw_value >= 10:
            return "Account has 10 or more posts."
        elif 5 <= raw_value <= 9:
            return "Account has 5 to 9 posts."
        elif 1 <= raw_value <= 4:
            return "Account has 1 to 4 posts."
        else:
            return "Account has 0 posts."

    elif variable_name == "follower_count":
        if raw_value >= 100:
            return "Account has 100 or more followers."
        elif 10 <= raw_value <= 99:
            return "Account has between 10 and 99 followers."
        else:
            return "Account has between 0 and 9 followers."

    elif variable_name == "following_count":
        if raw_value <= 100:
            return "Account follows between 0 and 100 accounts."
        elif 101 <= raw_value <= 500:
            return "Account follows between 101 and 500 accounts."
        else:
            return "Account follows more than 500 accounts."

    elif variable_name == "following_follower_ratio":
        if raw_value == float("inf"):
            return "Account follows others but has 0 followers."
        elif raw_value <= 1:
            return "Following/follower ratio is 1 or less."
        elif raw_value <= 3:
            return "Following/follower ratio is between 1 and 3."
        elif raw_value <= 10:
            return "Following/follower ratio is between 3 and 10."
        else:
            return "Following/follower ratio is greater than 10."

    elif variable_name == "private_status":
        if raw_value is True:
            return "Account is private."
        else:
            return "Account is public."

    elif variable_name == "username_structure":
        if raw_value == "normal":
            return "Username appears normal and readable."
        elif raw_value == "minor_numbers_symbols":
            return "Username contains minor numbers or symbols."
        elif raw_value == "random_pattern":
            return "Username contains a long numeric or random-looking pattern."
        else:
            return "Username appears highly random or automated."

    elif variable_name == "name_username_mismatch":
        if raw_value == "consistent":
            return "Display name and username are consistent."
        elif raw_value == "minor_variation":
            return "Display name and username are similar with minor variation."
        elif raw_value == "noticeable_mismatch":
            return "Display name and username show a noticeable mismatch."
        else:
            return "Display name and username appear completely inconsistent."

    elif variable_name == "links_in_bio":
        match_count = raw_value.get("match_count", 0)
        matched_terms = raw_value.get("matched_terms", [])
        if match_count == 0:
            return "No flagged link terms detected in bio links."
        return f"Flagged bio link terms detected: {', '.join(matched_terms)}."

    elif variable_name == "bio_content":
        bio_type = raw_value.get("bio_type", "normal")
        if bio_type == "normal":
            return "Bio appears normal."
        elif bio_type == "vague_minimal":
            return "Bio appears vague or minimal."
        elif bio_type == "generic_or_emoji_heavy":
            return "Bio appears generic or emoji-heavy."
        else:
            return "Bio contains propaganda or coordinated-style messaging."

    elif variable_name == "profile_picture_presence":
        if raw_value is True:
            return "Profile picture is present."
        else:
            return "Profile picture is missing or could not be confirmed."

    elif variable_name == "hashtags":
        total = raw_value.get("total_hashtags", 0)
        return f"{total} hashtag(s) detected in filtered comments."

    elif variable_name == "emoji_usage":
        total = raw_value.get("total_emojis", 0)
        return f"{total} emoji(s) detected in filtered comments."

    elif variable_name == "propaganda_phrases":
        total = raw_value.get("total_matches", 0)
        matched = raw_value.get("matched_phrases", [])
        if total == 0:
            return "No propaganda phrases detected."
        return f"{total} propaganda phrase match(es) detected: {', '.join(matched)}."

    elif variable_name == "emotional_language":
        total = raw_value.get("total_matches", 0)
        matched = raw_value.get("matched_words", [])
        if total == 0:
            return "No emotional language detected."
        return f"{total} emotional language match(es) detected: {', '.join(matched)}."

    elif variable_name == "country_mentions":
        total = raw_value.get("total_matches", 0)
        matched = raw_value.get("matched_terms", [])
        if total == 0:
            return "No country mentions detected."
        return f"{total} country mention(s) detected: {', '.join(matched)}."

    elif variable_name == "comment_length":
        avg = raw_value.get("average_length", 0)
        return f"Average filtered comment length is {avg:.2f} characters."

    elif variable_name == "punctuation_patterns":
        count = raw_value.get("pattern_count", 0)
        if count == 0:
            return "No repeated punctuation patterns detected."
        return f"{count} repeated punctuation pattern(s) detected."

    elif variable_name == "capitalization_patterns":
        count = raw_value.get("abnormal_count", 0)
        if count == 0:
            return "No abnormal capitalization patterns detected."
        return f"{count} abnormal capitalization pattern(s) detected."

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
def calculate_total_risk_score(variable_results):
    total_risk_score = 0

    for result in variable_results.values():
        total_risk_score += result["score"]

    return total_risk_score

# CALCULATE FINAL 0-99 SCORE
def calculate_final_score(total_risk_score):
    final_score = 99 - total_risk_score

    if final_score < 1:
        final_score = 1

    return final_score