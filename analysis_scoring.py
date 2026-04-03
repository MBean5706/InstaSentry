from analysis_compare import (
    compare_account_age,
    compare_username_changes,
    compare_post_count,
    compare_follower_count,
    compare_following_count,
    compare_following_follower_ratio
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