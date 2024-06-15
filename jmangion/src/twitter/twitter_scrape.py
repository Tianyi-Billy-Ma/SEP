import twikit
from twikit import Client
import time
import pandas as pd
import random
import json
import httpx

def write_data_to_file(data, filename):
    # write the data to file
    with open("./data/" + filename, 'w') as file:
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
        photos = [media for media in tweet.media if media['type'] == "photo"]
        try:
            post_structure['pic_id'] = photos[0]['id_str']
        except IndexError:
            pass
    post_structure['liked_users'] = [liker.id for liker in tweet.get_favoriters()]
    post_structure['keywords'] = []

    for liker in tweet.get_favoriters()[:25]: # only get the first 25 to avoid timeout error
        liker_relation = {}
        liker_relation['src_id'] = liker.id
        liker_relation['relation'] = "user-like-post"
        liker_relation['dest_id'] = tweet.id
        relations.append(liker_relation)

    for keyword in codes_dict_full.keys():
        if keyword in tweet.text.lower().split():
            post_structure['keywords'].append(codes_dict_full[keyword])

    for hashtag in tweet.hashtags:
        hashtag = hashtag.lower()
        if hashtag in codes_dict_full.keys():
            post_structure['keywords'].append(codes_dict_full[hashtag])

    # Eliminate duplicates
    post_structure['keywords'] = list(set(post_structure['keywords']))

    return post_structure



def read_codes():
    codes_df = pd.read_csv("newnewcodes.csv")
    # just get the last two columns for now, and the 13th-26th drugs (Leo will search 0-12)
    codes_df_jack = codes_df.iloc[13:26, 3:5]
    codes_df_full = codes_df.iloc[0:33, 3:5]

    # all keywords are standardized to lowercase for easier comparison since I will convert all search text to lowercase
    codes_dict_jack = {row[0].lower(): row[1] for row in codes_df_jack.itertuples(index=False, name=None)}
    codes_dict_full = {row[0].lower(): row[1] for row in codes_df_full.itertuples(index=False, name=None)}

    del codes_dict_jack['mescaline plug'] # already searched this
    del codes_dict_jack['meth plug'] # already searched this


    print("Using multiple rounds, this program will search over... ")
    for key in codes_dict_jack:
        print(key)
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

    if num_followers > 0:
        try:
            followers_list = client.get_user_followers(user.id, num_followers)
        except IndexError:
            followers_list = []
        followers_list = followers_list[:num_followers] # Manually limit the number of folowees to store (twikit fxn fails to do this)
    else:
        followers_list = []

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
    if num_followees > 0:
        try:
            followees_list = user.get_following(num_followees)
        except IndexError:
            followees_list = []
        followees_list = followees_list[:num_followees] # Manually limit the number of folowees to store (twikit fxn fails to do this)
    else:
        followees_list = []

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

def get_user_posts(client, user, num_posts, codes_dict_full, relations, posts, pictures, query):
    tweets_list = client.get_user_tweets(user.id, 'Tweets', num_posts)
    post_ids = []
    for tweet in tweets_list:
        # Store each reply to the tweet as a post structure
        post_replies = tweet.replies
        if post_replies is not None:
            for reply in post_replies:
                # add the comment to the relations structure
                user_make_comment = {}
                user_make_comment['src_id'] = reply.user.id
                user_make_comment['relation'] = "user-make-comment"
                user_make_comment['dest_id'] = reply.id
                relations.append(user_make_comment)

                comment_under_post = {}
                comment_under_post['src_id'] = reply.id
                comment_under_post['relation'] = "comment-under-post"
                comment_under_post['dest_id'] = tweet.id
                relations.append(comment_under_post)

                # make a post structure for each reply
                reply_post_struct = {}
                reply_post_struct['user_id'] = reply.user.id
                reply_post_struct['post_id'] = reply.id
                reply_post_struct['comment'] =  ""
                reply_post_struct['pic_id'] = ""
                if reply.media is not None:
                    photos_list = [media_item for media_item in reply.media if media_item['type'] == 'photo']
                    try:
                        reply_post_struct['pic_id'] = photos_list[0]['id_str']
                    except IndexError:
                        pass

                reply_post_struct['liked_users'] = [liker.id for liker in reply.get_favoriters()]
                reply_post_struct['comments'] = []
                if reply.replies is None:
                    reply_post_struct['user_comment'] = ""
                else:
                    for comment in reply.replies:
                        if comment.user.id == reply.user.id:
                            reply_post_struct['user_comment'] = comment.id
                        else:
                            reply_post_struct['comments'].append(comment.id)
                reply_post_struct['keywords'] = get_user_keywords(client, reply.user, None, codes_dict_full, query, relations)


                posts[reply.id] = reply_post_struct

        if tweet.media is not None:
            for media_item in tweet.media:
                if media_item['type'] == "photo":
                    picture = {}
                    picture['pic_id'] = media_item['id_str']
                    picture['post_id'] = tweet.id
                    picture['url'] = media_item['media_url_https']
                    pictures[media_item['id_str']] = picture
                    relations_struct = {}
                    relations_struct['src_id'] = tweet.id
                    relations_struct['relation'] = ['post-has-picture']
                    relations_struct['dest_id'] = media_item['id_str']
                    relations.append(relations_struct)
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

    if user.description is not None:
        # check the user's description for keywords and store them
        for line in user.description:
            relation_struct = {}
            for word in line.split():
                if word in codes_dict_full.keys():
                    user_keywords.append(codes_dict_full[word])
                    relation_struct["src_id"] = user.id
                    relation_struct["relation"] = "user-profile-keyword"
                    relation_struct["dest_id"] = codes_dict_full[word]
                    relations.append(relation_struct)

    # check the user's posts for keywords and store them
    if post_ids is not None:
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

    # ensure the original search query makes it into the keywords list -- removed this bc I don't want keyword to be associated with profile name
    # user_keywords.append(codes_dict_full[query])
    user_keywords = list(set(user_keywords)) # eliminate duplicates

    return user_keywords

def get_user_info(client, user, codes_dict_full, query, relations, posts, pictures, keywords):
    User_Structure = dict()
    User_Structure['username'] = user.name
    User_Structure['user_id'] = user.id
    User_Structure['followers'] = get_user_followers(client, user, relations, 10) # this fxn returns a list of follower ids. The last argument (# of followers to get) is adjustable
    User_Structure['followees'] = get_user_followees(client, user, relations, 10) # this fxn returns a list of followee ids. The last argument (# of followees to get) is adjustable
    User_Structure['profile_pic'] = user.profile_image_url
    User_Structure['profile_text'] = user.description
    User_Structure['posts'] = get_user_posts(client, user, 6, codes_dict_full, relations, posts, pictures, query)
    User_Structure['keywords'] = get_user_keywords(client, user, User_Structure['posts'], codes_dict_full, query, relations) # searches user profile and posts for keywords
    for user_keyword_id in User_Structure['keywords']:
        for key, value in codes_dict_full.items():
            if value == user_keyword_id:
                user_keyword_name = key
        try:
            established_keyword_struct = keywords[user_keyword_id] 
            established_keyword_struct['ids'].append(user.id)
        except KeyError:# if the keyword has no structure so far
            keywords_struct = {}

            keywords_struct['keyword'] = user_keyword_name
            keywords_struct['keyword_id'] = user_keyword_id
            keywords_struct['ids'] = []
            keywords_struct['ids'].append(user.id)
            keywords[user_keyword_id] = keywords_struct
            # if the keyword has been seen before
            keywords[user_keyword_id]['ids'].append(user.id)

    return User_Structure

def get_previous_data(filename):
    try:
        with open(filename, 'r') as f:
            data = json.load(f)
    except FileNotFoundError:
        # all structures are dictionaries, except for relations (which is a list)
        if filename != "relations.json":
            data = {}
        else:
            data = []

    return data

def deal_with_rate_limits(profile):
    profile = (profile + 1) % 4
    time.sleep(random.randint(1, 3))
    return profile

def record_completion_time(filename, query):
    # to avoid rate limits, run the program at least 15 minutes after the last run
    completion_time = time.strftime("%Y-%m-%d %H:%M:%S", time.localtime())
    with open(filename, "a") as file:
        file.write(f"Drug search for {query} completed at: {completion_time}\n")

def get_users_from_post_search(client, query, users_to_scrape):
    tweet_search_results = client.search_tweet(query, 'Top')
    tweet_searched_users = []
    # limit by number of users to retrieve
    for index, new_tweet in enumerate(tweet_search_results):
        if index > users_to_scrape:
            break
        tweet_searched_users.append(new_tweet.user)

    return tweet_searched_users

def main():
    """
    No longer a need to manually put the drug name in on each run... the program will automatically loop through every drug name and wait 15 minutes to avoid the rate
    limits. If the program stops, find out the last drug name that it stored and remove previous drug names from codes_dict_jack so that it picks up where it left off.
    """
    # use login_cookies (to save session) if possible, if that doesn't work, use the login_credentials() function

    total_users_scraped = 0
    codes_dict_jack, codes_dict_full = read_codes()
    for drug_name in codes_dict_jack:
    # users will be the dictionary that all User_Structures are stored in 
    # other structures also defined here
        users = get_previous_data("users.json")
        posts = get_previous_data("posts.json")
        pictures = get_previous_data("pictures.json")
        relations = get_previous_data("relations.json")
        keywords = get_previous_data("keywords.json")

        profile = 1
        client = login_cookies_user(profile)

        print("Drugs to be searched include: ")
        for drug in codes_dict_jack.keys():
            print(drug, end =', ')

        # Change the query each time to match the drug to be searched
        query = drug_name
        print(f"\nDrug being searched this time: {query}")
        time.sleep(random.randint(2, 10)) # waiting a bit to evade bot detection
        users_to_scrape = 150 # this is the maximum number of accounts to pull for each drug query.

        results = list(client.search_user(query, count = users_to_scrape)) # returns a list of the twikit.User class. If it can't find as many users as specified, it will just return as many as it can
        users_to_scrape -= len(results)
        tweet_search_results = get_users_from_post_search(client, query, users_to_scrape)

        print(f"{len(results)} users returned for direct user search on {query}")
        print(f"{len(tweet_search_results)} users returned from tweet search")
        results += tweet_search_results
        print(f"{len(results)} users returned for {query} in total:")
        for item in results:
            print(item.name, end = ', ')
        print("\n")
        print("sleeping for 15 minutes to avoid acct ban...")
        time.sleep(15*60)
        loopcount = 0
        repeats = 0
        for user in list(results):
            if loopcount % 25 == 0 and loopcount != 0: # waiting 15 mins to avoid rate limits
                print("hit checkpoint, writing data to files...")
                write_data_to_file(users, "users.json")
                write_data_to_file(posts, "posts.json")
                write_data_to_file(relations, "relations.json")
                write_data_to_file(pictures, "pictures.json")
                write_data_to_file(keywords, "keywords.json")
                record_completion_time("time.txt", query)
                print("sleeping 15 minutes to avoid rate limits... 30 examples have been searched without sleeping for {query} ")
                time.sleep(15*60)
                print("sleeping over. Recopying data from files...")
                users = get_previous_data("users.json")
                posts = get_previous_data("posts.json")
                pictures = get_previous_data("pictures.json")
                relations = get_previous_data("relations.json")
                keywords = get_previous_data("keywords.json")

            print("Looping through users...") if loopcount == 0 else None
            print(f"Scraping data from user {loopcount + 1} / {len(results)}")
            if f'user_{user.id}' in users: # skip profiles that have already been seen
                repeats += 1
                loopcount += 1
                print(f"user_{user.id} has already been scraped, skipping to next user")
                continue
            profile = deal_with_rate_limits(profile) # Switch profiles on every iteration of the loop to avoid rate limits
            client = login_cookies_user(profile)
            print(f"logged in profile {profile}!")
            time.sleep(random.randint(1,5))

            # get the data

            try:
                users[f'user_{user.id}'] = get_user_info(client, user, codes_dict_full, query, relations, posts, pictures, keywords) # this should return a user structure dictionary
            except httpx.ReadTimeout:
                print("hit httpx timeout, sleeping for 15 mins...")
                time.sleep(15*60)
                users[f'user_{user.id}'] = get_user_info(client, user, codes_dict_full, query, relations, posts, pictures, keywords) # this should return a user structure dictionary


            loopcount += 1
        total_users_scraped += (len(results) - repeats)
        print(f"attempted to scrape {len(results)} users using the query {query}")
        print(f"{repeats} / {len(results)} were already scraped and were skipped here")

        # write data to files periodically (after each drug search)
        write_data_to_file(users, "users.json")
        write_data_to_file(posts, "posts.json")
        write_data_to_file(relations, "relations.json")
        write_data_to_file(pictures, "pictures.json")
        write_data_to_file(keywords, "keywords.json")
        record_completion_time("time.txt", query)
        print(f"data for {query} saved to text files")
        print(f"{total_users_scraped} unique users scraped so far")
        print(f"sleeping for 15 minutes...")
        time.sleep(15 * 60)
        print("sleep over. Starting next drug search")

if __name__ == '__main__':
    main()

