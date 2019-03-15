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
    for post in red.subreddit("popular").hot(limit=500):
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
                    if search_result.score > 0.50:
                        found = True
                if not found:
                    post_images.append(post.url)
                    print(post.url)
                    f.write(post.url+"\n")
                else:
                    print("General Reposti")
                f.close()
        except Exception as e:
            print(e)
image_count = 0
batch_size = 32
counter = 0
current_batch = 0
with open("posts.txt") as f:
    images = [url.strip() for url in f]
    image_count = len(images)
while counter < image_count:
    print("Processing batch: #", (current_batch+1))
    imageList = []

    for current_index in range(counter, counter+batch_size - 1):
        try:
            imageList.append(ClImage(url=images[current_index]))
        except IndexError:
            break

    app.inputs.bulk_create_images(imageList)

    counter = counter + batch_size
    current_batch = current_batch + 1


# Check Visual Similarities

# Search using a URL
