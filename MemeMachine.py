import praw, prawcore

from clarifai.rest import ClarifaiApp, Image as ClImage
from config import meme_credentials, credentials as cred

class Classifier():
    def is_meme(self, url):
        app = ClarifaiApp(api_key=meme_credentials)
        search = app.inputs.search_by_image(url=url)
        for search_result in search:
            if search_result.score >= 0.95:
                print("Meme found: " + search_result.url)
                return True
        return False
    def get_template(self, url):
        app = ClarifaiApp(api_key=meme_credentials)
        search = app.inputs.search_by_image(url=url)
        for search_result in search:
            if search_result.score >= 0.95:
                return search_result.url
        return
    def is_safe(self, url):
        app = ClarifaiApp(api_key=meme_credentials)
        model = app.public_models.nsfw_model
        rating = model.predict_by_url(url)["outputs"][0]["data"]['concepts'][0]['value']
        return rating >= 0.97

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
