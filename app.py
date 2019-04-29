import datetime
import pickle
import praw
import prawcore
import requests
from clarifai.rest import ClarifaiApp
from clarifai.rest import Image as ClImage

from config import credentials as cred

app = ClarifaiApp(api_key=cred["api_key"])

#   flask_app = Flask(__name__)
red = praw.Reddit(
    username=cred["username"],
    password=cred["password"],
    client_id=cred["client_id"],
    client_secret=cred["client_secret"],
    user_agent=cred["user_agent"]
)


def reddit_url(s):
    return "https://www.reddit.com/" + s


post_images = repost_images = []

with open('posts.txt', 'a+') as f:  # I'll use a Pickle file in the future
    '''
    
    
        Sense a disturbance in Reddit, I have
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
        
    
    
    
    
    '''
    post: praw.reddit.models.Submission
    for post in red.subreddit(input("Subreddit:: ")).new(limit=int(input("Amount :: "))):
        """
        Meme this all you want but a lot of things can go wrong... that's why everything's surrounded by the try/catch block
        """
        try:
            response = requests.head(post.url)
            if "image" in response.headers.get('content-type'):
                found = False
                search = app.inputs.search_by_image(url=post.url)
                if len(search) == 0:
                    """ print("0 search results found.") -> Converted to if/else to cause program efficiency """
                else:
                    for search_result in search:
                        if search_result.score > 0.95:
                            found = True
                            if search_result.url == post.url:
                                print("Already in DB")
                            elif search_result.author.name == post.author.name:
                                print("User re-uploaded his/her own content")
                            else:
                                try:
                                    """
                                      This is a very bad practice --> Uploads the unique images to Clarifai
                                      with a batch size of 1. However, it's necessary if we want to actively
                                      compare values.
                                    """
                                    post.reply(
                                               "**General Reposti!**\n- If I\'m wrong, please downvote me -> Any reposts falsely downvoted will be added to the \"naughty list\"\n- If I\'m right, please upvote me\n- This message may have been sent due to re-uploading.\n-I'm not too good with memes\nI thought it was similar to this: {} (Post: {}). But I'm just a bot. I could be wrong.".format(search_result.url, "https://www.reddit.com/search?q=" + search_result.url))
                                except Exception as e:
                                    print("F&%!ing Rate Limit")
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
                                """.format(post.url, post.author, reddit_url(post.permalink), search_result.url))
                            continue
                if not found:
                    post_images.append(post.url)
                    print(post.url)
                    app.inputs.create_image(ClImage(url=post.url))
                    f.write(post.url+"\n")
        except prawcore.RequestException as e:
            """
            -------------------------
            Reddit Connection blocked
            -------------------------
            """
        except TypeError:
            """
            -------------------------
                 Not a text post
            -------------------------
            """
    f.close()
pickle.dump({
    "date": datetime.datetime.now(),
    "size": len(post_images),
    "posts": post_images
}, open("settings.reddit", "rb"))
