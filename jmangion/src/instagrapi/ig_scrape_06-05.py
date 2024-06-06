from instagrapi import Client
from instagrapi.exceptions import LoginRequired
import logging

def login_user(cl, logger):
    print("function called")
    """
    Attempts to login to Instagram using either the provided session information
    or the provided username and password.
    """
    with open("login.txt", "r") as f:
        USERNAME, PASSWORD = f.read().splitlines()
        print("login.txt opened")

    try:
        session = cl.load_settings("session.json")
    except FileNotFoundError:
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

    if not login_via_session:
        print("logging in with regular username and password")


        try:
            logger.info("Attempting to login via username and password. username: %s" % USERNAME)
            if cl.login(USERNAME, PASSWORD):
                login_via_pw = True
                cl.dump_settings("session.json")
        except Exception as e:
            logger.info("Couldn't login user using username and password: %s" % e)

    if not login_via_pw and not login_via_session:
        raise Exception("Couldn't login user with either password or session")

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


def main():
    logger = logging.getLogger()
    cl = Client()
    cl.delay_range = [2, 7]
    login_user(cl, logger)

    # get specified number of media (posts) based on hashtag search
    num_medias = 5
    medias = cl.hashtag_medias_top("computerscience", num_medias)
    print(f'number of medias scraped: {len(medias)} out of {num_medias}')

    #dictionary to hold all post structures
    posts = dict()
    for media in medias:
        post_structure = get_post_structure(cl, media)
        posts['media.pk'] = post_structure



    ## just printing for testing purposes
    for post_key, post_structure in posts.items():
        for key, value in post_structure:
            print(f'key: {key}, value: {value}')

if __name__ == '__main__' :
    main()
