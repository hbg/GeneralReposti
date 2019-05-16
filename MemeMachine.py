import praw, prawcore

from clarifai.rest import ClarifaiApp, Image as ClImage
from config import meme_credentials, credentials as cred

class Classifier():
    def __init__(self):
        app = ClarifaiApp(api_key=meme_credentials)
        """
        search = app.inputs.search_by_image(url=url)
        self.count = 0
        for search_result in search:
            if search_result.score >= threshold: self.count+=1
        """
    def is_meme(self, url):
        app = ClarifaiApp(api_key=meme_credentials)
        search = app.inputs.search_by_image(url=url)
        for search_result in search:
            if search_result.score >= 0.85:
                print("Meme found: " + search_result.url)
                return True
        return False
    def add_memes(self):
        red = praw.Reddit(**cred)
        app = ClarifaiApp(api_key=meme_credentials)
        meme_templates = red.subreddit('MemeTemplatesOfficial').top('all', limit=500)
        for template in meme_templates:
            print(template.url)
            search = app.inputs.search_by_image(url=template.url)
            found = False
            for search_item in search:
                if search_item.url == template.url: found = True
            if not found: app.inputs.create_image(ClImage(url=template.url))