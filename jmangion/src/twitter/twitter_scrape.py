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

    if tweet.replies == None:
        post_structure['user_comment'] = ""
    else:
        for comment in tweet.replies:
            if comment.user.id == user.id:
                post_structure['user_comment'] = comment.id
            else:
                post_structure['comments'].append(comment.id)

    if tweet.media == None:
        post_structure['pic_id'] = ""
    else:
        post_structure['pic_id'] = tweet.media[0]['id_str']
    post_structure['liked_users'] = [liker.id for liker in tweet.get_favoriters()]
    post_structure['keywords'] = []

    for line in tweet.text:
        for keyword in codes_dict_full.keys():
            if keyword in line:
                post_structure['keywords'].append(codes_dict_full[keyword])

    for hashtag in tweet.hashtags:
        if hashtag in codes_dict_full.keys():
            post_structure.append(codes_dict_full[keyword])

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

def login_credentials():
    print("attempting login with credentials...")
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
    print("attempting login in with cookies...")
    client = Client('en-US')
    client.load_cookies('cookies.json')
    return client

def get_user_followers(client, user, relations, max_followers):
    # get the first max_followers (10) followers 
    num_followers = user.followers_count
    if num_followers > max_followers:
        num_followers = max_followers
    #followers_list = user.get_followers(num_followers) # this function returns twikit.User objects
    if num_followers > 0:
        #followers_list = user.get_followers(num_followers)
        followers_list = client.get_user_followers(user.id, num_followers)
        #followers_list = client.get_user_followers(user.id, num_followers)
    else:
        followers_list = []
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
    return post_ids

def get_user_keywords(client, user, post_ids, codes_dict_full, query, relations):
    user_keywords = []

    # check the user's description for keywords and store them
    for line in user.description:
        relation_struct = {}
        for word in line.split():
            if word in codes_dict_full.keys():
                user_keywords.append(codes_dict_full[word])
                relation_struct["src_id"] = post.id
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
                relation_struct["src_id"] = post.id
                relation_struct["relation"] = "post-include-keyword"
                relation_struct["dest_id"] = codes_dict_full[hashtag]
                relations.append(relation_struct)

        # check the post's text
        for line in tweet.text:
            relation_struct = {}
            for word in tweet.text.split():
                if word in codes_dict_full.keys():
                    user_keywords.append(codes_dict_full[word])
                    relation_struct["src_id"] = post.id
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

def main():
    # use login_cookies (to save session) if possible, if that doesn't work, use the login_credentials() function
    #client = login_credentials()
    client = login_cookies()
    print("logged in!")
    codes_dict_jack, codes_dict_full = read_codes()
    # users will be the dictionary that all User_Structures are stored in 
    users = dict()
    posts = dict()
    comments = dict()
    relations = []
    #for drug_name in codes_dict_jack.keys(): # search the drug names that have been assigned to jack
    """
    due to rate limits I will now search one drug at a time rather than looping through each drug name
    """
    query = "oxy"
    time.sleep(random.randint(2, 10)) # waiting a bit to evade bot detection
    results = client.search_user(query, count = 10) # returns a list of the twikit.User class
    for user in results:
        users[f'user_{user.id}'] = get_user_info(client, user, codes_dict_full, query, relations, posts) # this should return a user structure dictionary

    # print out for debugging:
    print(json.dumps(users, indent=4))

    # write data to files
    write_data_to_file(users, "users.json")
    write_data_to_file(posts, "posts.json")
    write_data_to_file(relations, "relations.json")

if __name__ == '__main__':
    main()
