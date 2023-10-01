# Auto-Approval Bot Script
Source code to be run by auto-approval bot.

## Installation
- Install Python. You can download it here https://www.python.org/downloads/ (Add to PATH during the installation).  
- Download the ZIP file of this repo (Click on ```Code``` -> ```Download ZIP```).
- Unzip the ZIP file.
- Open your command prompt and change your directory to that of the unzipped files.  
- Install the required packages:  
  ```
  pip install -U praw
  ```
  
## Configuration
- Create a Reddit App (script) at https://www.reddit.com/prefs/apps/ and get your ```client_id``` and ```client_secret```.
- Edit the ```config.ini``` file with your details and save:
  ```
  [REDDIT]
  CLIENT_ID = your_client_id
  CLIENT_SECRET = your_client_secret
  PASSWORD = your_reddit_password
  USERNAME = your_reddit_username

  [VARS]
  PUBLIC_SUBREDDIT = public_subreddit_where_posts_will_be_checked
  ```

## Running the script
  ```
  python main.py
  ```
