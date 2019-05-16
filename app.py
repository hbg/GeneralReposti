import datetime
import pickle
import praw, prawcore
import requests
from clarifai.rest import ClarifaiApp, Image as ClImage
import clarifai
from config import credentials as cred

app = ClarifaiApp(api_key=cred["api_key"])
threshold = 0.975
amount = 15    # Scans 15 posts for now, but later it will be asynchronous
red = praw.Reddit(**cred)

def get_downvotes():
    """Check downvotes count for all posts"""
    u = red.redditor('generalrepostbot')
    for comment in u.comments.new(limit=None):
        print(comment.permalink)
        comment.refresh()
        if comment.score <= 0: comment.delete()
        for reply in comment.replies:
            if ("BAD" in reply.body.upper() and "BOT" in reply.body.upper()):
                print("I was not a good bot today")
                comment.delete()
get_downvotes()
def reddit_url(s):
    """Get converted Reddit URL"""
    return "https://www.reddit.com/" + s

with open("settings.reddit", "rb") as f:
    print(pickle.load(f))
post_images = repost_images = []

with open('posts.csv', 'a+') as f:  # I'll use a Pickle file in the future
    r'''
    
    
        Sense a disturbance in Reddit, I have...
                        ____
                     _.' :  `._
                 .-.'`.  ;   .'`.-.
        __      / : ___\ ;  /___ ; \      __
      ,'_ ""--.:__;".-.";: :".-.":__;.--"" _`,
      :' `.t""--.. '<@.`;_  ',@>` ..--""j.' `;
           `:-.._J '-.-'L__ `-- ' L_..-;'
             "-.__ ;  .-"  "-.  : __.-"
                 L ' /.------.\ ' J
                  "-.   "--"   .-"
                 __.l"-:_JL_;-";.__
              .-j/'.;  ;""""  / .'\"-.
            .' /:`. "-.:     .-" .';  `.
         .-"  / ;  "-. "-..-" .-"  :    "-.
      .+"-.  : :      "-.__.-"      ;-._   \
      ; \  `.; ;                    : : "+. ;
      :  ;   ; ;                    : ;  : \:
     : `."-; ;  ;                  :  ;   ,/;
      ;    -: ;  :                ;  : .-"'  :
      :\     \  : ;             : \.-"      :
       ;`.    \  ; :            ;.'_..--  / ;
       :  "-.  "-:  ;          :/."      .'  :
         \       .-`.\        /t-""  ":-+.   :
          `.  .-"    `l    __/ /`. :  ; ; \  ;
            \   .-" .-"-.-"  .' .'j \  /   ;/
             \ / .-"   /.     .'.' ;_:'    ;
              :-""-.`./-.'     /    `.___.'
                    \ `t  ._  /  bug :F_P:
                     "-.t-._:'
        
    
    
    
    Future Plan: Add 'anti-repost' which takes memes in from r/dankmemes, r/memes, and r/prequelmemes to
    find meme formats (which it currently identifies as reposts)

    This is how it'll work (pseudocode obv)
    if not is_meme(image_url):
        do {everything}
    '''
    post: praw.reddit.models.Submission
    posts = list(red.subreddit('memes').new(limit=threshold)
    posts.reverse()
    for post in posts:
        """
        Meme this all you want but a lot of things can go wrong... that's why everything's surrounded by the try/catch block
        """
        try:
            response = requests.head(post.url)
            if "image" in response.headers.get('content-type'):
                found = False
                search = app.inputs.search_by_image(url=post.url)
                max_value = 0
                if len(search) is not 0:
                    for search_result in search:
                        if search_result.score > threshold:
                            found = True
                            max_value = search_result.score
                            if search_result.url == post.url:
                                print("Already in DB")
                            else:
                                try:
                                    """
                                      This is a very bad practice --> Uploads the unique images to Clarifai
                                      with a batch size of 1. However, it's necessary if we want to actively
                                      compare values.
                                    """
                                    post.reply(
                                              '''**General Reposti!**\n- If I\'m wrong, please downvote me -> Any reposts falsely downvoted will be added to the \"naughty list\"\n- If I\'m right, please upvote me\n- This message may have been sent due to re-uploading.\n- I'm not too good with memes, but\n- I thought it was similar to this: {} (Post: {}). But I'm just a bot. I could be wrong.'''.format(search_result.url, "https://www.reddit.com/search?q=" + search_result.url))
                                    
                                except Exception as e:
                                    print("F&%!ing Rate Limit:" + e)
                                # -> That's a bluff, I don't have a naughty list
                                print("""
                                Repost Found:
                                ________________
                                |
                                |   url: {}
                                |   author: {}
                                |   image url: {}
                                |   similar to: {}
                                |
                                |_______________
                                """.format(post.url, post.author, reddit_url(post.permalink), search_result.url))
                            continue
                if not found:
                    print("OC: " + post.url + str(max_value)) # OC Badge
                    post_images.append(post.url)
                    app.inputs.create_image(ClImage(url=post.url))
                f.write("{},{}\n".format(post.url, max_value))
        except prawcore.RequestException as e:
            print("Connection couldn't be established")
            """
            -----------------------------
            | Reddit Connection blocked |
            -----------------------------
            """
        except TypeError as e:
            print("The post given is a textpost")
            """
            -------------------------
            |    Is a text post     |
            -------------------------
            """
        except clarifai.errors.ApiError:
            print("Failed uploading")
            """
            ---------------------------------------
            |   Most likely due to GIF content    |
            ---------------------------------------
            """
    f.close()
pickle.dump({
    "date": str(datetime.datetime.now().strftime("%m,%d,%Y,%H,%M,%S")),
    "size": len(post_images),
    "posts": post_images
}, open("settings.reddit", "wb"))
