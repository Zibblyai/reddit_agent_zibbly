import praw
import openai
import requests
import gspread
from google.oauth2.service_account import Credentials
from datetime import datetime
import os
from dotenv import load_dotenv

load_dotenv()

# --- CONFIGURATION ---

# Reddit API
REDDIT_CLIENT_ID = os.getenv("REDDIT_CLIENT_ID")
REDDIT_CLIENT_SECRET = os.getenv("REDDIT_CLIENT_SECRET")
REDDIT_USER_AGENT = os.getenv("REDDIT_USER_AGENT")

# OpenAI API
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")
openai.api_key = OPENAI_API_KEY

# Slack
SLACK_WEBHOOK_URL = os.getenv("SLACK_WEBHOOK_URL")
ENABLE_SLACK = os.getenv("ENABLE_SLACK", "True") == "True"

# Subreddits (can stay hardcoded or be turned into an ENV var)
SUBREDDITS = ["dogs", "puppy101"]

# Google Sheet
GOOGLE_SHEET_CREDENTIALS = "zibbly-credentials.json"  # this is fine if it's mounted
SPREADSHEET_ID = os.getenv("SPREADSHEET_ID")
WORKSHEET_NAME = os.getenv("WORKSHEET_NAME")

# --- FUNCTIONS ---

def run_reddit_agent(query: str):
    # your agent logic
    return "result from Reddit"

def connect_sheet():
    scope = ["https://www.googleapis.com/auth/spreadsheets"]
    creds = Credentials.from_service_account_file(GOOGLE_SHEET_CREDENTIALS, scopes=scope)
    client = gspread.authorize(creds)
    return client.open_by_key(SPREADSHEET_ID).worksheet(WORKSHEET_NAME)

def log_to_sheet(post, comment):
    sheet = connect_sheet()
    sheet.append_row([
        datetime.now().strftime("%B %d %Y"),
        f"r/{post.subreddit.display_name}",
        post.title,
        f"https://reddit.com{post.permalink}",
        post.score,
        post.num_comments,
        comment,
        "Pending",
        ""
    ])

def get_posts():
    reddit = praw.Reddit(
        client_id=REDDIT_CLIENT_ID,
        client_secret=REDDIT_CLIENT_SECRET,
        user_agent=REDDIT_USER_AGENT
    )
    posts = []
    for sub in SUBREDDITS:
        for post in reddit.subreddit(sub).hot(limit=5):
            if not post.stickied and post.num_comments > 5:
                posts.append(post)
    return posts

def generate_reply(title, body):
    prompt = f"""
You’re Zibbly — imagine you're a real pet parent who happens to work on an app that helps other dog owners.

Zibbly gives breed-specific tips, tracks routines, and turns daily care into fun tasks — but don't pitch it unless it fits naturally.

Now write a short, helpful Reddit reply under 350 characters to this post. Keep it casual and human — like a dog-loving friend chiming in. If it makes sense, mention Zibbly in a low-key way (like “that’s actually something Zibbly helps me with”).

Reddit post:
Title: {title}
Body: {body[:500]}

Write the reply:
    """
    res = openai.ChatCompletion.create(
        model="gpt-4",
        messages=[{"role": "user", "content": prompt}],
        temperature=0.7
    )
    return res.choices[0].message.content.strip()

def send_to_slack(post, comment):
    text = f"""🐶 *New Reddit Post from r/{post.subreddit.display_name}*
*Title:* {post.title}
*Link:* https://reddit.com{post.permalink}
*Upvotes:* {post.score}
*Comments:* {post.num_comments}

📝 *Zibbly Reply:*
```{comment}```
"""
    if ENABLE_SLACK:
        response = requests.post(SLACK_WEBHOOK_URL, json={"text": text})
        if response.status_code != 200:
            print("Slack error:", response.text)
    else:
        print("🔕 Slack disabled – here's what would've been sent:\n", text)

# --- MAIN ---

def main():
    print("🐾 Running Reddit + GPT + Slack + Google Sheet Agent...\n")
    posts = get_posts()
    for post in posts:
        comment = generate_reply(post.title, post.selftext)
        print(f"\n🔗 {post.title} (r/{post.subreddit.display_name})")
        print(f"📝 {comment}\n")
        send_to_slack(post, comment)
        log_to_sheet(post, comment)

if __name__ == "__main__":
    main()



