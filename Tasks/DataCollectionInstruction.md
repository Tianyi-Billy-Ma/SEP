Data Collection on Social Media Instructions
============================================

* We define five types of data: user, post, comment, picture, and keyword(including emoji), and 11 types of relations among them, (data-relation-data):
  * user-follow/followed-user: the user follows or followed by another user.
  * user-tag-user: the user tags another user in a post.
  * user-mention-user: the user mentions another user in a post.
  * user-like-post: the user likes the post.
  * user-publish-post: the user publishes a post (plaintext). 
  * user-profile-keyword: the user has the keyword in the profile.
  * user-make-comment: the user makes the comment.
  * comment-under-post: the comment is under the post.
  * comment-contain-keyword: the comment includes the keyword.
  * post-has-picture: the post has the picture.
  * post-include-keyword: the post includes the keyword.



We start by searching posts by keywords, i.e., keywords/hashtags of keywords in the post content. With the collected posts, we can get a group of users who publish these posts. For simplicity, let's call these users "seed users". Then we can collect the related users of the seed users based on the relations defined above. We will repeat this process couple of times until we reach the desired number of positive users, i.e., ~1500 users per platform.

* For each social media user, sometimes, it is impossible to collect all related users, as the user may have too many followers, followees or replies. In this case, you can selectively collect the most relevant related users for each relation type under criteria: i.e., the top 30 followers that have the keyword in their posts/profile/username, etc. 
* Keep all collected data (user, post, comment, and pics), even if is not used in the final dataset. Because we also need to have some negative data to train the model.
* For Instagram, if the time is limited, we can give up on pictures download, but we still need to keep the URLs and the relationships between the pictures and the posts.
* For better readability, please revise the id of the data with the prefix of the data type, e.g., user_id_from_twitter = "123456", then user_id = "user_123456", post_id_from_instagram = "151551", then post_id = "post_151551".
* For keywords in data leave it empty if not match any keywords, and please create the keyword_id for each keyword, e.g., keyword_id = "keyword_1"(This should be consistent among different platforms).

Data Structure
===========================================

```python
User_Structure = {
    "username": str,
    "user_id": str, 
    "followers": ["user_id1", "user_id2", "user_id3", ...],
    "followees": ["user_id1", "user_id2", "user_id3", ....],
    "profile_pic": "xxxxx.jpg",
    "posts": ["post_id1", "post_id2", ...]  ,
    "keywords": [ str, str, str, ... ] 
}
Post_Structure = {
     "user_id": str,
    "post_id": str,
    "user_comment": str,
    "pic": "xxxxx.jpg",
    "liked_users": [ "user_id1", "user_id2", "user_id3", ...],
    "comments": ["comment_id1", "comment_id2", "comment_id3", ... ],
    "keywords": [str, str, str, ...],
}
Comment_Structure = {
    "comment_id": str,
    "user_id": str,
    "post_id": str,
    "comment": str,
    "keywords": [str, str, str, ...],
}
Picture_Structure = {
    "pic_id": str,
    "post_id": str,
    "url": "xxxxx.jpg",
}
Keyword_Structure = {
    "keyword": str,
    "keyword_id": str,
    "ids": [ "user_id1", "user_id2", ..., "post_id1", "post_id2", ... "comment_id1", "comment_id2", ..., "pic_id1", "pic_id2", ... ]
}
Relation_Structure = {
    "src_id": str,
    "relation": str,
    "dest_id": str,
}
```

The saved json files should be named as "user.json", "post.json", "comment.json", "picture.json", "keyword.json", "relation.json".

```python
#user.json
users = {
    "user_id": User_Structure,
}
#post.json
posts = {
    "post_id": Post_Structure,
}
#comment.json
comments = {
    "comment_id": Comment_Structure,
}
#picture.json
pictures = {
    "pic_id": Picture_Structure,
}
#keyword.json
keywords = {
    "keyword_id": Keyword_Structure,
}

```    






