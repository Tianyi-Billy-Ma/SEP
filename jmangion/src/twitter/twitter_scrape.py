import twikit
from twikit import Client
import time
import pandas as pd
import random
import json

def write_data_to_file(data, filename):
    # write the data to file
    with open(filename, 'w') as file:
        # Write the data to the file in JSON format
        json.dump(data, file, indent=4)


def get_post_info(client, user, tweet, codes_dict_full, relations):
    post_structure = {}
    post_structure['user_id'] = user.id
    post_structure['post_id'] = tweet.id
    post_structure['comments'] = []

    if tweet.replies is None:
        post_structure['user_comment'] = ""
    else:
        for comment in tweet.replies:
            if comment.user.id == user.id:
                post_structure['user_comment'] = comment.id
            else:
                post_structure['comments'].append(comment.id)

    if tweet.media is None:
        post_structure['pic_id'] = ""
    else:
        post_structure['pic_id'] = tweet.media[0]['id_str']
    post_structure['liked_users'] = [liker.id for liker in tweet.get_favoriters()]
    post_structure['keywords'] = []

    for keyword in codes_dict_full.keys():
        if keyword in tweet.text:
            post_structure['keywords'].append(codes_dict_full[keyword])

    for hashtag in tweet.hashtags:
        if hashtag in codes_dict_full.keys():
            post_structure['keywords'].append(codes_dict_full[keyword])

    # Eliminate duplicates
    post_structure['keywords'] = list(set(post_structure['keywords']))

    return post_structure



def read_codes():
    codes_df = pd.read_csv("drug_codes.csv")
    # just get the last two columns for now, and the 13th-26th drugs (Leo will search 0-12)
    codes_df_jack = codes_df.iloc[13:26, 3:]
    print("Searching for")
    print(codes_df_jack)
    codes_df_full = codes_df.iloc[:26, 3:]
    codes_dict_jack = {row[0]: row[1] for row in codes_df_jack.itertuples(index=False, name=None)}
    codes_dict_full = {row[0]: row[1] for row in codes_df_full.itertuples(index=False, name=None)}
    return codes_dict_jack, codes_dict_full

def login_credentials(profile):
    print(f"attempting login profile {profile} with credentials...")
    client = Client('en-US')
    with open(f"login{profile}.txt", "r") as f:
        USERNAME, EMAIL, PASSWORD = f.read().splitlines()
        print("read login information")
    client.login(
        auth_info_1=USERNAME ,
        auth_info_2=EMAIL,
        password=PASSWORD
    )
    print(f"storing cookies in cookies{profile}.json")
    client.save_cookies(f'cookies{profile}.json')
    return client

def login_cookies_user(profile):
    print(f"attempting login profile {profile} in with cookies...")
    client = Client('en-US')
    client.load_cookies(f'cookies{profile}.json')
    return client

def get_user_followers(client, user, relations, max_followers):
    # get the first max_followers (10) followers 
    num_followers = user.followers_count
    if num_followers > max_followers:
        num_followers = max_followers
    #followers_list = user.get_followers(num_followers) # this function returns twikit.User objects
    #followers_list = user.get_followers(num_followers)
    followers_list = client.get_user_followers(user.id, num_followers)
    followers_list = followers_list[:num_followers] # Manually limit the number of folowees to store (twikit fxn fails to do this)
    #followers_list = client.get_user_followers(user.id, num_followers)
    followers_id_list = []
    for follower_user in followers_list:
        followers_id_list.append(follower_user.id)
        # the next block is all for relation
        relation_struct = {}
        relation_struct["src_id"] = user.id
        relation_struct["relation"] = "user-followed-by-user"
        relation_struct["dest_id"] = follower_user.id
        relations.append(relation_struct)
    return followers_id_list

def get_user_followees(client, user, relations, max_followees):
    num_followees = user.following_count
    if num_followees > max_followees:
        num_followees = max_followees
    followees_list = client.get_user_following(user.id, num_followees) # this function returns twikit.User objects
    followees_list = followees_list[:num_followees] # Manually limit the number of folowees to store (twikit fxn fails to do this)
    followees_id_list = []
    for followee_user in followees_list:
        followees_id_list.append(followee_user.id)
        # the next block is all for relation
        relation_struct = {}
        relation_struct["src_id"] = user.id
        relation_struct["relation"] = "user-follows-user"
        relation_struct["dest_id"] = followee_user.id
        relations.append(relation_struct)
    return followees_id_list

def get_user_posts(client, user, num_posts, codes_dict_full, relations, posts):
    tweets_list = client.get_user_tweets(user.id, 'Tweets', num_posts)
    post_ids = []
    for tweet in tweets_list:
        posts[tweet.id] = get_post_info(client, user, tweet, codes_dict_full, relations)
        post_ids.append(tweet.id)
        relation_struct = {}
        relation_struct["src_id"] = user.id
        relation_struct["relation"] = "user-publish-post"
        relation_struct["dest_id"] = tweet.id
        relations.append(relation_struct)
    return post_ids

def get_user_keywords(client, user, post_ids, codes_dict_full, query, relations):
    user_keywords = []

    # check the user's description for keywords and store them
    for line in user.description:
        relation_struct = {}
        for word in line.split():
            if word in codes_dict_full.keys():
                user_keywords.append(codes_dict_full[word])
                relation_struct["src_id"] = user.id
                relation_struct["relation"] = "profile-include-keyword"
                relation_struct["dest_id"] = codes_dict_full[word]
                relations.append(relation_struct)

    # check the user's posts for keywords and store them
    for post_id in post_ids:
        tweet = client.get_tweet_by_id(post_id)

        #check the post's hashtags
        for hashtag in tweet.hashtags:
            relation_struct = {}
            if hashtag in codes_dict_full.keys():
                user_keywords.append(codes_dict_full[hashtag])
                relation_struct["src_id"] = post_id
                relation_struct["relation"] = "post-include-keyword"
                relation_struct["dest_id"] = codes_dict_full[hashtag]
                relations.append(relation_struct)

        # check the post's text
            for word in tweet.text.split():
                relation_struct = {}
                if word in codes_dict_full.keys():
                    user_keywords.append(codes_dict_full[word])
                    relation_struct["src_id"] = post_id
                    relation_struct["relation"] = "post-include-keyword"
                    relation_struct["dest_id"] = codes_dict_full[word]
                    relations.append(relation_struct)

    user_keywords = list(set(user_keywords)) # eliminate duplicates

    if query not in user_keywords:
        user_keywords.append(query)
    return user_keywords

def get_user_info(client, user, codes_dict_full, query, relations, posts):
    User_Structure = dict()
    User_Structure['username'] = user.name
    User_Structure['user_id'] = user.id
    User_Structure['followers'] = get_user_followers(client, user, relations, 10) # this fxn returns a list of follower ids. The last argument (# of followers to get) is adjustable
    User_Structure['followees'] = get_user_followees(client, user, relations, 10) # this fxn returns a list of followee ids. The last argument (# of followees to get) is adjustable
    User_Structure['profile_pic'] = user.profile_image_url
    User_Structure['profile_text'] = user.description
    User_Structure['posts'] = get_user_posts(client, user, 6, codes_dict_full, relations, posts)
    User_Structure['keywords'] = get_user_keywords(client, user, User_Structure['posts'], codes_dict_full, query, relations) # searches user profile and posts for keywords
    return User_Structure

def get_previous_data(filename):
    try:
        with open(filename, 'r') as f:
            data = json.load(f)
    except FileNotFoundError:
        if filename != "relations.json":
            data = {}
        else:
            data = []

    return data

def deal_with_rate_limits(profile):
    profile = (profile + 1) % 3
    time.sleep(random.randint(1, 3))
    return profile

def record_completion_time(filename):
    completion_time = time.strftime("%Y-%m-%d %H:%M:%S", time.localtime())
    with open(filename, "a") as file:
        file.write(f"Program completed at: {completion_time}\n")


def main():
    """
    due to rate limits I will now search one drug at each run of the program rather than looping through each drug name.
    This means I will manually put a drug from codes_dict_jack.keys() into the program on each run
    """
    # use login_cookies (to save session) if possible, if that doesn't work, use the login_credentials() function

    """
    TEMPORARY TO ESTABLISH COOKIES
    client = login_credentials(1)
    client = login_credentials(2)
    return
    """

    codes_dict_jack, codes_dict_full = read_codes()
    # users will be the dictionary that all User_Structures are stored in 
    # other structures also defined here
    users = get_previous_data("users.json")
    posts = get_previous_data("posts.json")
    comments = get_previous_data("comments.json")
    relations = get_previous_data("relations.json")

    profile = 0
    client = login_cookies_user(profile)

    print("Drugs to be searched include: ")
    for drug in codes_dict_jack.keys():
        print(drug, end =', ')

    # Change the query each time to match the drug to be searched
    query = "shrooms"
    print(f"\nDrug being searched this time: {query}")
    time.sleep(random.randint(2, 10)) # waiting a bit to evade bot detection
    users_to_scrape = 15
    results = client.search_user(query, count = users_to_scrape) # returns a list of the twikit.User class
    loopcount = 0
    repeats = 0
    for user in results:
        if loopcount == 0:
            print("Looping through users...")
        print(f"Scraping data from user {loopcount} / {users_to_scrape}")
        if f'user_{user.id}' in users: # skip profiles that have already been seen
            repeats += 1
            print(f"user_{user.id} has already been scraped, skipping to next user")
            continue
        profile = deal_with_rate_limits(profile) # Switch profiles on every iteration of the loop to avoid rate limits
        client = login_cookies_user(profile)
        print(f"logged in profile {profile}!")
        time.sleep(random.randint(1,2))

        # get the data
        users[f'user_{user.id}'] = get_user_info(client, user, codes_dict_full, query, relations, posts) # this should return a user structure dictionary
        loopcount += 1

    print(f"attempted to scrape {users_to_scrape} users using the query {query}")
    print(f"{repeats} / {users_to_scrape} were already scraped and were skipped here")

    # write data to files
    write_data_to_file(users, "users.json")
    write_data_to_file(posts, "posts.json")
    write_data_to_file(relations, "relations.json")
    record_completion_time("time.txt")

if __name__ == '__main__':
    main()
