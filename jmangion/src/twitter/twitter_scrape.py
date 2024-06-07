import twikit
from twikit import Client
import time
import pandas as pd
import random
import json

def read_codes():
    codes_df = pd.read_csv("drug_codes.csv")
    # just get the last two columns for now, and the 13th-26th drugs (Leo will search 0-12)
    codes_df_jack = codes_df.iloc[13:26, 3:]
    print(codes_df_jack)
    codes_df_full = codes_df.iloc[:26, 3:]
    return codes_df_jack.to_dict(), codes_df_full.to_dict()

def login_credentials():
    print("attempting login with credentials")
    client = Client('en-US')
    with open("login.txt", "r") as f:
        USERNAME, EMAIL, PASSWORD = f.read().splitlines()
        print("stored login information")
    client.login(
        auth_info_1=USERNAME ,
        auth_info_2=EMAIL,
        password=PASSWORD
    )
    print("storing cookies in cookies.json")
    client.save_cookies('cookies.json')
    return client

def login_cookies():
    print("attempting login in with cookies")
    client = Client('en-US')
    client.load_cookies('cookies.json')
    return client

def get_user_followers(user, num_followers):
    followers_list = user.get_followers(num_followers) # this function returns twikit.User objects
    followers_id_list = []
    for follower_user in followers_list:
        followers_id_list.append(follower_user.id)
    return followers_id_list

def get_user_followees(user, num_followees):
    followees_list = user.get_following(num_followees) # this function returns twikit.User objects
    followees_id_list = []
    for followee_user in followees_list:
        followees_id_list.append(followee_user.id)
    return followees_id_list

def get_user_posts(client, user, num_posts):
    tweets_list = client.get_user_tweets(user.id, 'Tweets', num_posts)
    post_ids = []
    for tweet in tweets_list:
        post_ids.append(tweet.id)
    return post_ids

def get_user_keywords(client, user, post_ids, codes_dict_full, query):
    user_keywords = []

    # check the user's description for keywords and store them
    for line in user.description:
        for word in line.split():
            if word in codes_dict_full.keys():
                user_keywords.append(codes_dict_full[word])

    # check the user's posts for keywords and store them
    for post_id in post_ids:
        tweet = client.get_tweet_by_id(post_id)

        #check the post's hashtags
        for hashtag in tweet.hashtags:
            if hashtag in codes_dict_full.keys():
                user_keywords.append(codes_dict_full[hashtag])

        # check the post's text
        for line in tweet.text:
            for word in tweet.text.split():
                if word in codes_dict_full.keys():
                    user_keywords.append(codes_dict_full[word])

    user_keywords = list(set(user_keywords)) # eliminate duplicates

    if query not in user_keywords:
        user_keywords.append(query)
    return user_keywords

def get_user_info(client, user, codes_dict_full, query):
    User_Structure = dict()
    User_Structure['username'] = user.name
    User_Structure['user_id'] = user.id
    User_Structure['followers'] = get_user_followers(user, 10) # this fxn returns a list of follower ids. The last argument (# of followers to get) is adjustable
    User_Structure['followees'] = get_user_followees(user, 10) # this fxn returns a list of followee ids. The last argument (# of followees to get) is adjustable
    User_Structure['profile_pic'] = user.profile_image_url
    User_Structure['profile_text'] = user.description
    User_Structure['posts'] = get_user_posts(client, user, 6)
    User_Structure['keywords'] = get_user_keywords(client, user, User_Structure['posts'], codes_dict_full, query) # searches user profile and posts for keywords
    return User_Structure

def main():
    # use login_cookies (to save session) if possible, if that doesn't work, use the login_credentials() function
    # client = login_credentials()
    client = login_cookies()
    print("logged in!")
    codes_dict_jack, codes_dict_full = read_codes()
    # users will be the dictionary that all User_Structures are stored in 
    users = dict()
    for drug_name in codes_dict_jack.keys(): # search the drug names that have been assigned to jack
        query = drug_name
        time.sleep(random.randint(2, 10)) # waiting a bit to evade bot detection
        results = client.search_user(query, count = 10) # returns a list of the twikit.User class
        for user in list(results):
            users[user.id] = get_user_info(client, user, codes_dict_full, query) # this should return a user structure dictionary

    # print out for debugging:
    print(json.dumps(users, indent = 4))

if __name__ == '__main__':
    main()
