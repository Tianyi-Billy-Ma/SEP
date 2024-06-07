from instagrapi import Client
from instagrapi.exceptions import LoginRequired
import logging
from fp.fp import FreeProxy
import re

def login_user(cl, logger):
    print("login function called")
    """
    Attempts to login to Instagram using either the provided session information
    or the provided username and password.
    """
    with open("login.txt", "r") as f:
        USERNAME, PASSWORD = f.read().splitlines()
        print("login.txt opened and login information stored")

    try:
        session = cl.load_settings("session.json")
    except FileNotFoundError:
        print("Could not find session.json")
        session = False

    login_via_session = False
    login_via_pw = False
    if session:
        print("there is a session")
        try:
            cl.set_settings(session)
            cl.login(USERNAME, PASSWORD)

            # check if session is valid
            try:
                print("checking if session is valid")
                cl.get_timeline_feed()
            except LoginRequired:
                logger.info("Session is invalid, need to login via username and password")

                old_session = cl.get_settings()

                # use the same device uuids across logins
                cl.set_settings({})
                cl.set_uuids(old_session["uuids"])
                print("logging in with username and password, but keeping old uuids")
                cl.login(USERNAME, PASSWORD)
            login_via_session = True
        except Exception as e:
            logger.info("Couldn't login user using session information: %s" % e)
            print("couldn't lgin user using session information: %s" % e)

    if not login_via_session:
        print("logging in with regular username and password without uuids")


        try:
            logger.info("Attempting to login via username and password. username: %s" % USERNAME)
            if cl.login(USERNAME, PASSWORD):
                login_via_pw = True
                cl.dump_settings("session.json")
                print("dumped settings to session.json")
        except Exception as e:
            logger.info("Couldn't login user using username and password: %s" % e)

    if not login_via_pw and not login_via_session:
        raise Exception("Couldn't login user with either password or session")
        print("Error!! Couldn't login using session or regular login")

def get_post_structure(cl, media):
    # getting data in dictionary format for copying
    media_dict = media.dict()
    comments = cl.media_comments(media_id=media.pk)

    # data structure to hold post info:
    post_structure = dict()
    post_structure['user_id'] = media_dict['user']['pk']
    post_structure['post_id'] = media_dict['pk']
    # post_structure['user_comment'] handled below
    # post_structure['pic_id'] handled below
    post_structure['comments'] = [] # handled below
    post_structure['keywords'] = media_dict['usertags']

    # dealing with comments: need to separate the user comment from others
    comments = cl.media_comments(media_id=media.pk)
    for comment in comments:
        # Check if the comment is from the user who made the post
        if comment.user.pk == media_dict['user']['pk']:
            post_structure['user_comment'] = comment.text
            comments.remove(comment) # exclude user comment from list of commments
    post_structure['comments'] = comments

    for resource in media_dict['resources']:
        if resource['media_type'] == 1:
            # then this is a picture
            post_structure['pid_id'] =  resource['pk']
            break

    return post_structure

def get_user_structure(cl, media):
    '''
    User_Structure = {
    "username": str,
    "user_id": str,
    "followers": ["user_id1", "user_id2", "user_id3", ...],
    "followees": ["user_id1", "user_id2", "user_id3", ....],
    "profile_pic": "xxxxx.jpg",
    "profile_text: str,
    "posts": ["post_id1", "post_id2", ...]  ,
    "keywords": [ keyword_id1, keyword_id2, keyword_id3, ... ]
    }
    '''

    media_dict = media.dict()
    user_structure = dict()
    user_structure['username'] = media_dict['usertags']['username']
    user_structure['user_id'] = media_dict['usertags']['pk']
    user_structure['followers'] = [] # filled out below
    user_structure['followees'] = [] # filled out below
    user_structure['profile_pic'] =  media_dict['user']['profile_pic_url'].url
    user_structure['profile_text'] =  cl.user_info_by_username(user_structure['username'].dict()['biography'])

    user_medias = cl.user_medias(user_structure['user_id'], amount=6)
    post_ids = [media.id for media in medias]
    user_structure['posts'] = post_ids
    user_structure['keywords'] = [] # filled below
    hashtags = []
    for user_media in user_medias:
        if media.caption_text:
            hashtags.extend(re.findall(r"#\w+", media.caption_text))

    hashtags = sorted(list(set(hashtags)))
    user_structure['keywords'] = hashtags

    followers_dict = user_followers(media_dict['usertags']['pk'], 30) # select 30 followers
    for followerID in followers_dict.keys():
        user_structure['followers'].append(followerID)

    followees_dict = user_following(media_dict['usertags']['pk'], 30) # select 30 followees
    for followeeID in folowees_dict.keys():
        user_structure['followees'].append(followeeID)

def get_comments(cl, media):
    pass




def main():
    logger = logging.getLogger()
    cl = Client()
    cl.set_user_agent("Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/125.0.0.0 Safari/537.36")
    #ip = FreeProxy().get()
    """
    before_ip = cl._send_public_request(url="https://api.ipify.org/")
    """
    #cl.set_proxy(dsn=ip)
    """
    after_ip = cl._send_public_request(url="https://api.ipify.org/")
    print(f"before ip: {before_ip}")
    print(f"after ip: {after_ip}")
    """
    cl.delay_range = [2, 7] # extended delay range
    #login_user(cl, logger)

    # get specified number of media (posts) based on hashtag search
    num_medias = 5
    medias = cl.hashtag_medias_top("programming", num_medias)
    print(f'number of medias scraped: {len(medias)} out of {num_medias}')
    return
    #dictionary to hold all post structures
    posts = dict()
    for media in medias:
        post_structure = get_post_structure(cl, media)
        posts['media.pk'] = post_structure


    """
    users = dict()
    for media in medias:
        user_structure = get_user_structure(cl, media)

    comments = dict()
    for media in medias:
        get_comments(cl, media)
    """


    ## just printing for testing purposes
    for post_key, post_structure in posts.items():
        for key, value in post_structure:
            print(f'key: {key}, value: {value}')

if __name__ == '__main__' :
    main()
