from flask import Flask, request, jsonify, send_file
from io import BytesIO
from flask_cors import CORS
import os
from config import MAX_NO_NEW_SCROLLS
from insta_browser import (
    open_instagram_login,
    is_instagram_logged_in,
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
    save_comments_to_file,
    save_data_to_json,
    extract_top_level_comments,
    filter_comments_by_keywords,
    get_comments_by_username
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
    build_score_breakdown,
    build_display_name_presence_result,
    build_repetitive_comment_pattern_result,
    evaluate_combo_rules,
    build_why_report,
    get_confidence_label
)

app = Flask(__name__)
CORS(app)

# BACKEND SESSION STATE
backend_state = {
    "driver": None,
    "post_url": None,
    "comment_limit": None,
    "keywords": [],
    "comments": [],
    "filtered_comments": [],
    "user_comments": [],
    "profile_data": None,
    "about_data": None,
    "score_breakdown": None,
    "final_score": None
}

# PROFILE-ONLY PROGRESS STATE
profile_progress = {
    "steps": [
        {"name": "Searching profile...", "status": "pending"},
        {"name": "Collecting public profile data...", "status": "pending"},
        {"name": "Scoring account indicators...", "status": "pending"},
        {"name": "Preparing result files...", "status": "pending"}
    ]
}

# OUTPUT FILE NAMES
ALL_COMMENTS_TXT = "all_comments.txt"
FILTERED_COMMENTS_TXT = "filtered_comments.txt"
ALL_COMMENTS_JSON = "all_comments.json"
FILTERED_COMMENTS_JSON = "filtered_comments.json"
PROFILE_DATA_JSON = "profile_data.json"
ABOUT_DATA_JSON = "about_account_data.json"
PROFILE_ACCOUNT_JSON = "profile_account_data.json"
SCORE_BREAKDOWN_JSON = "score_breakdown.json"
WHY_REPORT_TXT = None

# GET OR START BROWSER SESSION
def get_driver():
    if backend_state["driver"] is None:
        backend_state["driver"] = open_instagram_login()
    return backend_state["driver"]

# RESET ANALYSIS-SPECIFIC STATE
def reset_analysis_state():
    backend_state["post_url"] = None
    backend_state["comment_limit"] = None
    backend_state["keywords"] = []
    backend_state["comments"] = []
    backend_state["filtered_comments"] = []
    backend_state["user_comments"] = []
    backend_state["profile_data"] = None
    backend_state["about_data"] = None
    backend_state["score_breakdown"] = None
    backend_state["final_score"] = None

# RESET PROFILE-ONLY PROGRESS
def reset_profile_progress():
    profile_progress["steps"] = [
        {"name": "Searching profile...", "status": "pending"},
        {"name": "Collecting public profile data...", "status": "pending"},
        {"name": "Scoring account indicators...", "status": "pending"},
        {"name": "Preparing result files...", "status": "pending"}
    ]

# SET PROFILE-ONLY PROGRESS STEP
def set_profile_progress(step_index, status):
    if 0 <= step_index < len(profile_progress["steps"]):
        profile_progress["steps"][step_index]["status"] = status

# BUILD VARIABLE RESULTS
def build_variable_results(profile_data, about_data, user_comments):
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
        variable_results["display_name_presence"] = build_display_name_presence_result(profile_data)
        variable_results["name_username_mismatch"] = build_name_username_mismatch_result(profile_data)
        variable_results["links_in_bio"] = build_links_in_bio_result(profile_data)
        variable_results["bio_content"] = build_bio_content_result(profile_data)
        variable_results["profile_picture_presence"] = build_profile_picture_presence_result(profile_data)

    if user_comments:
        variable_results["hashtags"] = build_hashtags_result(user_comments)
        variable_results["emoji_usage"] = build_emoji_usage_result(user_comments)
        variable_results["propaganda_phrases"] = build_propaganda_phrases_result(user_comments)
        variable_results["emotional_language"] = build_emotional_language_result(user_comments)
        variable_results["country_mentions"] = build_country_mentions_result(user_comments)
        variable_results["comment_length"] = build_comment_length_result(user_comments)
        variable_results["punctuation_patterns"] = build_punctuation_patterns_result(user_comments)
        variable_results["capitalization_patterns"] = build_capitalization_patterns_result(user_comments)
        variable_results["repetitive_comment_pattern"] = build_repetitive_comment_pattern_result(user_comments)

    return variable_results

# SAVE CURRENT OUTPUT FILES
def save_current_outputs(profile_data=None, about_data=None, score_breakdown=None):
    if backend_state["comments"]:
        save_comments_to_file(backend_state["comments"], ALL_COMMENTS_TXT)
        save_data_to_json(backend_state["comments"], ALL_COMMENTS_JSON)

    if backend_state["filtered_comments"]:
        save_comments_to_file(backend_state["filtered_comments"], FILTERED_COMMENTS_TXT)
        save_data_to_json(backend_state["filtered_comments"], FILTERED_COMMENTS_JSON)

    if profile_data is not None:
        save_data_to_json(profile_data, PROFILE_DATA_JSON)

    if about_data is not None:
        save_data_to_json(about_data, ABOUT_DATA_JSON)
        save_data_to_json({
            "profile": profile_data,
            "about_account": about_data
        }, PROFILE_ACCOUNT_JSON)

    if score_breakdown is not None:
        save_data_to_json(score_breakdown, SCORE_BREAKDOWN_JSON)

def save_text_to_file(text, filename):
    try:
        base_dir = os.path.dirname(os.path.abspath(__file__))
        file_path = os.path.join(base_dir, filename)

        with open(file_path, "w", encoding="utf-8") as file:
            file.write(text)

        return file_path

    except Exception as e:
        print(f"Failed to save text file: {e}")
        return None

# HEALTH CHECK
@app.route("/health", methods=["GET"])
def health_check():
    return jsonify({"status": "ok"})

# START LOGIN SESSION
@app.route("/start-login", methods=["POST"])
def start_login():
    driver = get_driver()

    if driver is None:
        return jsonify({
            "success": False,
            "message": "Failed to open Instagram login page."
        }), 500

    return jsonify({
        "success": True,
        "message": "Instagram login session is ready."
    })

# CHECK LOGIN STATUS
@app.route("/login-status", methods=["GET"])
def login_status():
    driver = backend_state["driver"]

    if driver is None:
        return jsonify({
            "success": False,
            "logged_in": False,
            "message": "Instagram browser session has not been started."
        }), 400

    logged_in = is_instagram_logged_in(driver)

    return jsonify({
        "success": True,
        "logged_in": logged_in
    })

# GET PROFILE-ONLY PROGRESS
@app.route("/profile-progress", methods=["GET"])
def get_profile_progress():
    return jsonify(profile_progress)

# VALIDATE USERNAME BEFORE PROFILE ANALYSIS
@app.route("/validate-username", methods=["POST"])
def validate_username():
    data = request.get_json() or {}
    username = str(data.get("username", "")).strip().replace("@", "")

    if username == "" or " " in username:
        return jsonify({
            "success": False,
            "valid": False,
            "message": "Invalid username. Please try again."
        }), 400

    driver = get_driver()

    if driver is None:
        return jsonify({
            "success": False,
            "valid": False,
            "message": "Could not start Instagram browser session."
        }), 500

    profile_loaded = load_profile_page(driver, username)

    if not profile_loaded:
        return jsonify({
            "success": True,
            "valid": False,
            "message": "Username not found. Please try again."
        })

    return jsonify({
        "success": True,
        "valid": True,
        "message": "Username accepted."
    })

# RUN FULL ANALYSIS COMMENT COLLECTION
@app.route("/full-analysis/start", methods=["POST"])
def full_analysis_start():
    data = request.get_json() or {}

    post_url = str(data.get("post_url", "")).strip()
    comment_limit = data.get("comment_limit")
    keywords = data.get("keywords", [])

    if post_url == "" or "instagram.com" not in post_url:
        return jsonify({
            "success": False,
            "message": "Invalid Instagram post URL."
        }), 400

    try:
        comment_limit = int(comment_limit)
    except Exception:
        return jsonify({
            "success": False,
            "message": "Comment limit must be a whole number."
        }), 400

    if comment_limit < 1 or comment_limit > 1000:
        return jsonify({
            "success": False,
            "message": "Comment limit must be between 1 and 1000."
        }), 400

    if not isinstance(keywords, list):
        return jsonify({
            "success": False,
            "message": "Keywords must be sent as a list."
        }), 400

    cleaned_keywords = [str(word).strip().lower() for word in keywords if len(str(word).strip()) >= 2]

    if len(cleaned_keywords) == 0:
        return jsonify({
            "success": False,
            "message": "At least one valid keyword is required."
        }), 400

    driver = get_driver()

    if driver is None:
        return jsonify({
            "success": False,
            "message": "Could not start Instagram browser session."
        }), 500

    reset_analysis_state()

    backend_state["post_url"] = post_url
    backend_state["comment_limit"] = comment_limit
    backend_state["keywords"] = cleaned_keywords

    post_loaded = load_post_after_login(driver, post_url)

    if not post_loaded:
        return jsonify({
            "success": False,
            "message": "Could not load the Instagram post."
        }), 400

    scroll_container = find_scrollable_comment_container(driver)

    if scroll_container is None:
        return jsonify({
            "success": False,
            "message": "No scrollable comment container found."
        }), 400

    comments_container = find_comments_container(driver)
    time_elements = find_comment_candidates(comments_container)
    no_new_scrolls = 0

    while len(time_elements) < comment_limit and no_new_scrolls < MAX_NO_NEW_SCROLLS:
        before_count = len(time_elements)

        scroll_comment_container(scroll_container)

        comments_container = find_comments_container(driver)
        time_elements = find_comment_candidates(comments_container)

        after_count = len(time_elements)

        if after_count > before_count:
            no_new_scrolls = 0
        else:
            no_new_scrolls += 1

    comments = extract_top_level_comments(time_elements, sample_limit=comment_limit)
    filtered_comments = filter_comments_by_keywords(comments, cleaned_keywords)

    backend_state["comments"] = comments
    backend_state["filtered_comments"] = filtered_comments

    save_current_outputs()

    return jsonify({
        "success": True,
        "message": "Comments collected successfully.",
        "comments_collected": len(comments),
        "filtered_comments_found": len(filtered_comments)
    })

# RUN PROFILE ANALYSIS
@app.route("/profile-analysis/run", methods=["POST"])
def profile_analysis_run():
    data = request.get_json() or {}

    username = str(data.get("username", "")).strip().replace("@", "")
    analysis_mode = str(data.get("analysis_mode", "profile")).strip().lower()

    reset_profile_progress()

    if username == "" or " " in username:
        return jsonify({
            "success": False,
            "message": "Invalid username. Please try again."
        }), 400

    driver = get_driver()

    if driver is None:
        return jsonify({
            "success": False,
            "message": "Could not start Instagram browser session."
        }), 500

    user_comments = []

    try:
        # STEP 1: SEARCH PROFILE
        set_profile_progress(0, "in_progress")

        if analysis_mode == "full":
            user_comments = get_comments_by_username(backend_state["filtered_comments"], username)

        profile_loaded = load_profile_page(driver, username)

        if not profile_loaded:
            set_profile_progress(0, "failed")
            return jsonify({
                "success": False,
                "message": "Invalid username or unavailable Instagram page."
            }), 400

        set_profile_progress(0, "complete")

        # STEP 2: COLLECT PUBLIC PROFILE DATA
        set_profile_progress(1, "in_progress")

        profile_data = extract_basic_profile_data(driver, username)

        if profile_data is None:
            set_profile_progress(1, "failed")
            return jsonify({
                "success": False,
                "message": "Failed to extract public profile data."
            }), 500

        about_data = None
        menu_opened = open_profile_details_menu(driver)

        if menu_opened:
            about_data = extract_about_account_data(driver)

        set_profile_progress(1, "complete")

        # STEP 3: SCORE ACCOUNT INDICATORS
        set_profile_progress(2, "in_progress")

        from analysis_compare import (
            compare_post_count,
            compare_follower_count,
            compare_following_count,
            compare_following_follower_ratio,
            compare_bio_content,
            compare_links_in_bio,
            compare_account_age,
            compare_username_changes
        )

        data = {
            "posts": compare_post_count(profile_data),
            "followers": compare_follower_count(profile_data),
            "following": compare_following_count(profile_data),
            "ratio": compare_following_follower_ratio(profile_data),
            "bio_type": compare_bio_content(profile_data).get("bio_type"),
            "emoji": compare_bio_content(profile_data).get("emoji_count", 0),
            "link_flag": compare_links_in_bio(profile_data).get("match_count", 0),
            "account_age": compare_account_age(about_data),
            "username_changes": compare_username_changes(about_data)
        }

        variable_results = build_variable_results(profile_data, about_data, user_comments)

        combo_result = evaluate_combo_rules(data)
        triggered_combos = combo_result["triggered_combos"]

        total_risk_score = calculate_total_risk_score(variable_results, data)
        final_score = calculate_final_score(total_risk_score)
        score_breakdown = build_score_breakdown(variable_results, total_risk_score, final_score)

        score_breakdown["username"] = username
        score_breakdown["confidence"] = get_confidence_label(final_score)
        score_breakdown["triggered_combos"] = triggered_combos

        backend_state["user_comments"] = user_comments
        backend_state["profile_data"] = profile_data
        backend_state["about_data"] = about_data
        backend_state["score_breakdown"] = score_breakdown
        backend_state["final_score"] = final_score
        backend_state["username"] = username
        backend_state["triggered_combos"] = triggered_combos
        backend_state["total_risk_score"] = total_risk_score
        backend_state["variable_results"] = variable_results

        set_profile_progress(2, "complete")

        # STEP 4: PREPARE RESULT FILES
        set_profile_progress(3, "in_progress")

        save_current_outputs(profile_data, about_data, score_breakdown)

        set_profile_progress(3, "complete")

        return jsonify({
            "success": True,
            "message": "Profile analysis completed successfully.",
            "final_score": final_score,
            "risk_score": total_risk_score,
            "matched_user_comments": len(user_comments),
            "score_breakdown": score_breakdown
        })

    except Exception as e:
        for i, step in enumerate(profile_progress["steps"]):
            if step["status"] == "in_progress":
                set_profile_progress(i, "failed")
                break

        return jsonify({
            "success": False,
            "message": f"Profile analysis failed: {e}"
        }), 500

# DOWNLOAD OUTPUT FILES
@app.route("/download/<file_key>", methods=["GET"])
def download_file(file_key):
    file_map = {
        "all_comments": ALL_COMMENTS_TXT,
        "filtered_comments": FILTERED_COMMENTS_TXT,
        "profile_data": PROFILE_DATA_JSON
    }

    if file_key == "why_report":
        username = backend_state.get("username")
        final_score = backend_state.get("final_score")
        total_risk_score = backend_state.get("total_risk_score")
        variable_results = backend_state.get("variable_results")
        triggered_combos = backend_state.get("triggered_combos")

        if not username or final_score is None or total_risk_score is None or variable_results is None:
            return jsonify({
                "success": False,
                "message": "No why report available yet. Run analysis first."
            }), 404

        why_report_text = build_why_report(
            username=username,
            final_score=final_score,
            total_risk_score=total_risk_score,
            variable_results=variable_results,
            triggered_combos=triggered_combos or []
        )

        why_report_filename = f"why_report_{username}.txt"

        memory_file = BytesIO(why_report_text.encode("utf-8"))
        memory_file.seek(0)

        return send_file(
            memory_file,
            as_attachment=True,
            download_name=why_report_filename,
            mimetype="text/plain"
        )

if __name__ == "__main__":
    app.run(host="127.0.0.1", port=5000, debug=False)