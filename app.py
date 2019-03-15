from flask import Flask
from config import credentials as cred
import requests
from clarifai.rest import Image as ClImage
from clarifai.rest import ClarifaiApp
import praw, time


app = ClarifaiApp(api_key=cred["api_key"])

#   flask_app = Flask(__name__)
red = praw.Reddit(
    username=cred["username"],
    password=cred["password"],
    client_id=cred["client_id"],
    client_secret=cred["client_secret"],
    user_agent=cred["user_agent"]

)
post_images, repost_images = [],[]
with open('posts.txt', 'a+') as f:
    for post in red.subreddit("popular").new(limit=500):
        try:
            response = requests.head(post.url)
            type = response.headers.get('content-type')
            similar = False
            if not similar and "image" in type:
                found = False
                search = app.inputs.search_by_image(url=post.url)
                if len(search) == 0:
                    """ print("0 search results found.") """
                for search_result in search:
                    if search_result.score > 0.90:
                        found = True
                        if search_result.url == post.url:
                            print("Already in DB")
                        else:
                            post.reply(
                                       """
                                       **General Reposti!**
                                       I thought it was similar to this: {}. But I'm just a bot. I could be wrong.
                                       """.format(search_result.url))
                            print("General Reposti")
                if not found:
                    post_images.append(post.url)
                    print(post.url)
                    app.inputs.create_image(ClImage(url=post.url))
                    f.write(post.url+"\n")
        except Exception as e:
            print(e)
    f.close()
batch_size = round(len(post_images/10))
current_batch, counter, image_count = [0]*3
images = [url.strip() for url in post_images]
image_count = len(post_images)

# I'll admit... this next part was fetched from the Clarifai documentation
"""
while counter < image_count:
    imageList = []

    for current_index in range(counter, counter+batch_size - 1):
        try:
            imageList.append(ClImage(url=images[current_index]))
        except IndexError:
            break

    app.inputs.bulk_create_images(imageList)

    counter = counter + batch_size
    current_batch += 1
red.__exit__()
"""