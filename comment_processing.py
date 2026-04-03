import re
import json
from selenium.webdriver.common.by import By

# EXTRACT STRUCTURED TOP-LEVEL COMMENTS
def extract_top_level_comments(time_elements, sample_limit=20):
    try:
        comments = []
        seen = set()

        for time_element in time_elements:
            try:
                candidate_block = time_element.find_element(By.XPATH,
                    "./ancestor::div[count(.//time)=1][3]")

                block_text = candidate_block.text.strip()

                if block_text == "":
                    continue

                if block_text in seen:
                    continue

                seen.add(block_text)

                lines = [line.strip() for line in block_text.split("\n") if line.strip() != ""]

                if len(lines) < 3:
                    continue

                author = lines[0]
                comment_time = lines[1]
                comment_text = " ".join(lines[2:])

                comments.append({
                    "author": author,
                    "time": comment_time,
                    "text": comment_text
                })

                if len(comments) >= sample_limit:
                    break

            except Exception:
                continue

        print(f"\nStructured top-level comments extracted: {len(comments)}")
        return comments

    except Exception as e:
        print(f"\nError: Could not extract structured comments. {e}")
        return []

# PRINT STRUCTURED COMMENTS
def print_structured_comments(comments, sample_count=10):
    try:
        print("\n--- STRUCTURED TOP-LEVEL COMMENTS ---")

        max_samples = min(sample_count, len(comments))

        for i in range(max_samples):
            print(f"\nComment {i + 1}:")
            print(f"Author: {comments[i]['author']}")
            print(f"Time:   {comments[i]['time']}")
            print(f"Text:   {comments[i]['text']}")

    except Exception as e:
        print(f"\nError: Could not print structured comments. {e}")

# FILTER COMMENTS BY KEYWORDS (WHOLE WORD / PHRASE MATCHING)
def filter_comments_by_keywords(comments, keywords):
    try:
        filtered_comments = []

        for comment in comments:
            comment_text = comment["text"].lower()
            matched_keywords = []

            for keyword in keywords:
                keyword = keyword.lower().strip()

                # MULTI-WORD PHRASE = direct match
                if " " in keyword:
                    if keyword in comment_text:
                        matched_keywords.append(keyword)

                # SINGLE WORD = whole word match using regex
                else:
                    pattern = r"\b" + re.escape(keyword) + r"\b"
                    if re.search(pattern, comment_text):
                        matched_keywords.append(keyword)

            if len(matched_keywords) > 0:
                filtered_comments.append({
                    "author": comment["author"],
                    "time": comment["time"],
                    "text": comment["text"],
                    "matched_keywords": matched_keywords
                })

        print(f"\nFiltered comments found: {len(filtered_comments)}")
        return filtered_comments

    except Exception as e:
        print(f"\nError: Could not filter comments by keywords. {e}")
        return []

# PRINT FILTERED COMMENTS
def print_filtered_comments(filtered_comments):
    try:
        print("\n--- FILTERED STRUCTURED TOP-LEVEL COMMENTS ---")

        if len(filtered_comments) == 0:
            print("No comments matched the selected keywords.")
            return

        for i, comment in enumerate(filtered_comments, start=1):
            print(f"\nFiltered Comment {i}:")
            print(f"Author: {comment['author']}")
            print(f"Time:   {comment['time']}")
            print(f"Text:   {comment['text']}")
            print(f">> Matched Keywords: {', '.join(comment['matched_keywords'])}")

    except Exception as e:
        print(f"\nError: Could not print filtered comments. {e}")

# SAVE COMMENTS TO FILE
def save_comments_to_file(comments, filename):
    try:
        with open(filename, "w", encoding="utf-8") as file:
            for i, comment in enumerate(comments, start=1):
                file.write(f"Comment {i}:\n")
                file.write(f"Author: {comment['author']}\n")
                file.write(f"Time:   {comment['time']}\n")
                file.write(f"Text:   {comment['text']}\n")

                if "matched_keywords" in comment:
                    file.write(f"Matched Keywords: {', '.join(comment['matched_keywords'])}\n")

                file.write("\n" + "-"*40 + "\n\n")

        print(f"\nSaved {len(comments)} comments to {filename}")

    except Exception as e:
        print(f"\nError saving comments to file: {e}")

# SAVE ALL DATA TO JSON FILE
def save_data_to_json(data, filename):
    try:
        with open(filename, "w", encoding="utf-8") as file:
            json.dump(data, file, indent=4, ensure_ascii=False)

        print(f"\nSaved data to {filename}")

    except Exception as e:
        print(f"\nError saving JSON data to file: {e}")