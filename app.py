import datetime
import pickle
import praw, prawcore
import requests
import time
from clarifai.rest import ClarifaiApp, Image as ClImage
import clarifai
from config import credentials as cred
from MemeMachine import Classifier
app = ClarifaiApp(api_key=cred["api_key"])
threshold = 0.975
meme_threshold = 0.99
amount = 1000    # Scans 15 posts for now, but later it will be asynchronous
red = praw.Reddit(**cred)
meme_identifier = Classifier()
# meme_identifier.add_memes()
def get_downvotes():
    """Check downvotes count for all posts"""
    u = red.redditor('generalrepostbot')
    for comment in u.comments.top(limit=None):
        print(comment.permalink)
        comment.refresh()
        if comment.score <= 0: comment.delete()
        for reply in comment.replies:
            print("|----> Comment: {}".format(reply.body))
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
    --> Working on this now, currently have 220 meme formats.
    '''
    post: praw.reddit.models.Submission
    posts = list(red.subreddit('memes').new(limit=amount))
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
                        if search_result.score >= threshold:
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
                                              '''**General Reposti!**\n- If I\'m wrong, please downvote me -> Any reposts falsely downvoted will be added to the \"naughty list\"\n- If I\'m right, please upvote me\n- This message may have been sent due to re-uploading.\n- I'm not too good with memes, but I thought it was similar to this: {} (Post: {}). But I'm just a bot. I could be wrong.'''.format(search_result.url, "https://www.reddit.com/search?q=url:" + search_result.url))
                                    
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
                meme = meme_identifier.is_meme(post.url)
                safety_rating = True
                if not found or meme and max_value >= meme_threshold:
                    safety_rating = meme_identifier.is_safe(post.url)
                    print("OC: " + post.url + " Score: " + str(max_value) + ". Safe? " + str(safety_rating)) # OC Badge
                    if safety_rating:
                        post_images.append(post.url)
                        app.inputs.create_image(ClImage(url=post.url))
                    else:
                        print("NSFW post... that's nasty")
                if meme:
                    print("I thought this was a meme: " + post.url)
                    post.reply("Nice meme! I see you used this format: {}. I'm on a hunt to find OC (as a bot, of course) and deemed your meme original content. If you want this comment deleted, please reply \"BAD BOT.\" ".format(meme_identifier.get_template(post.url))) 
                f.write("{},{},{}\n".format(post.url, max_value, safety_rating))
        except prawcore.RequestException as e:
            print("Connection couldn't be established")
            """
            -----------------------------
            | Reddit Connection blocked |
            -----------------------------
            """
        except praw.exceptions.APIException:
            print("Rate limit for Reddit reached. Will wait 10 minutes.")
            time.sleep(600)
        except TypeError as e:
            print(e)
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
