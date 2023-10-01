from utils import config_util, reddit_util, database_util
import logging
import prawcore
import time
import threading
import re
from praw import models, exceptions

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    datefmt='%Y-%m-%d %H:%M:%S',
    filename="run.log"
)

connection = database_util.connect_to_db()
config = config_util.load_config()
reddit = reddit_util.initialize_reddit(config)

# Checks if subreddit exists.
def validate_subreddit(subreddit_name: str):
    if subreddit_name.strip() == '' or subreddit_name is None:
        return None
    
    try:
        return reddit.subreddits.search_by_name(subreddit_name, exact=True)[0]
    except prawcore.exceptions.NotFound:
        return None

# Keeps track of all posts made to request for addition to the subreddit network.
def store_request_posts(subreddit: models.Subreddit):
    print("Checking for request posts...")

    for post in subreddit.stream.submissions():
        try:
            if post.link_flair_text is None or post.link_flair_text.lower() != "request":
                continue

            logging.info("New request post found.")
            print("New request post found.")
            database_util.insert_request_post(connection, post)
        except prawcore.exceptions.NotFound:
            continue

# Goes through all request posts and approves users who have been greenlit by mods.
def approve_users():
    print("Checking for users to approve...")

    while True:
        request_post_ids = database_util.retrieve_request_posts(connection)
        restricted_subreddits = database_util.retrieve_restricted_subreddits(connection)

        for id in request_post_ids:
            try:
                post = reddit.submission(id[0])
                post.title # Fetches the full submission

                new_flair = post.link_flair_text.lower().strip()
                if new_flair != "complete" and new_flair != "approved":
                    continue

                post_author = post.author
                logging.info(f"Adding {post_author} to restricted subreddits.")
                for sub_name in restricted_subreddits:
                    sub = reddit.subreddit(sub_name[0])
                    sub.contributor.add(post_author.name)
                    time.sleep(2)
                
                database_util.insert_approved_user(connection, post_author.name)
                database_util.remove_request_post(connection, post)

                post.reply("Your request has been approved by the mods. You have been added to the restricted subreddits.")
                logging.info(f"Successfully added {post_author} to restricted subreddits.")
            except prawcore.exceptions.NotFound:
                continue

        time.sleep(2 * 60)

def check_for_mod_invites():
    print("Checking for mod invites...")

    mod_invite_message_regex = r"invitation to moderate /r/([^/]+)"

    while True:
        for item in reddit.inbox.unread(limit=None):
            if not isinstance(item, models.Message):
                continue

            mod_invite_message_match = re.search(mod_invite_message_regex, item.subject)
            if mod_invite_message_match is None:
                continue

            # Accept mod invite
            subreddit_name = mod_invite_message_match.group(1)
            sub = reddit.subreddit(subreddit_name)
            # Just incase an accepted invite wasn't marked as read, somehow.
            try:
                sub.mod.accept_invite()
            except exceptions.RedditAPIException:
                continue

            print(f"Accepted mod invite to {subreddit_name}.")
            logging.info(f"Successfully accepted mod invite to {subreddit_name}.")

            # Add subreddit to list of restricted subs
            database_util.insert_restricted_subreddit(connection, subreddit_name)
            print(f"Added {subreddit_name} to list of restricted subreddits.")
            logging.info(f"{subreddit_name} has been added to the list of restricted subreddits.")

            item.mark_read()

            # Add all approved users to the subreddit
            logging.info(f"Adding all approved users to {subreddit_name}.")
            print(f"Adding all approved users to {subreddit_name}.")
            approved_users = database_util.retrieve_approved_users(connection)
            for user in approved_users:
                sub.contributor.add(user[0])
                time.sleep(2)

        time.sleep(2 * 60)

if __name__ == "__main__":
    subreddit_name = config['VARS']['PUBLIC_SUBREDDIT']
    subreddit = validate_subreddit(subreddit_name)
    if not subreddit:
        logging.error(f"Subreddit does not exist: r/{subreddit_name}.")
        print(f"Subreddit does not exist: r/{subreddit_name}.")
        exit()

    if not subreddit.user_is_moderator:
        logging.error(f"You must be a mod in this sub: r/{subreddit_name}.")
        print(f"You must be a mod in this sub: r/{subreddit_name}.")
        exit()

    threading.Thread(target=store_request_posts, args=(subreddit,)).start()
    threading.Thread(target=approve_users).start()
    threading.Thread(target=check_for_mod_invites).start()