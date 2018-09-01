import sys, os, time, requests, json
from datetime import datetime
from timeit import default_timer as timer
try:
    from humanfriendly import format_timespan
except ImportError:
    def format_timespan(seconds):
        return "{:.2f} seconds".format(seconds)

import logging
logging.basicConfig(format='%(asctime)s %(name)s.%(lineno)d %(levelname)s : %(message)s',
        datefmt="%H:%M:%S",
        level=logging.INFO)
# logger = logging.getLogger(__name__)
logger = logging.getLogger('__main__').getChild(__name__)

class AnnotatorBot(object):

    """Bot to create annotations on documents"""

    def __init__(self, app_context, name, api_url=None):
        """

        :app_context: flask app context
        :name: name of AnnotatorBot (e.g., 'AnnotatorBot1'. Must have an account on the app already.)

        """
        self.app_context = app_context
        self.name = name
        if api_url is None:
            api_url = "{}/api".format(os.environ.get('HYPOTHESIS_SERVICE'))
        self.api_url = api_url

    def _get_username(self, name=None, authority='sciencehistory.org'):
        if name is None:
            name = self.name
        return "acct:{}@{}".format(name, authority)

    @staticmethod
    def _get_new_annotation_params(target, text, uri, group='Kzwy6GDV', tags=[]):
        """Get the parameters for a new annotation request.

        :target: TextQuoteSelector dictionary of {'exact': <text to match>, 'prefix': 32-character prefix, 'suffix': 32-character suffix}
        :text: text of the annotation to add
        :uri: URI of the document
        :group: annotation group
        :tags: tags for the new annotation
        :returns: dictionary of request parameters

        """
        target['type'] = 'TextQuoteSelector'
        a = {
            'group': group,
            'permissions': {'read': ['group:{}'.format(group)]},
            'tags': tags,
            'target': [{'selector': [
                target
            ]}],
            'text': text,
            'uri': uri,
        }
        return a

    def _get_token_params(self, username=None):
        """Get the parameters to request JWT token to authorize further API requests

        :username: username for the token
        :returns: dictionary of request parameters

        """
        if username is None:
            username = self.name
        token = self.app_context.app.hypothesis_client.grant_token(username=username)
        params = {
            'assertion': token.decode(),
            'grant_type': 'urn:ietf:params:oauth:grant-type:jwt-bearer',
        }
        return params

    def get_access_token(self, username=None):
        """Get the access token to authorize further API requests

        :username: username for the token
        :returns: token

        """
        params = self._get_token_params(username=username)
        r = requests.post(self.api_url + "/token", params=params)
        return r.json()['access_token']

    def _authorize(self):
        """get authorization headers
        :returns: dict

        """
        access_token = self.get_access_token()
        headers = {"Authorization": "Bearer {}".format(access_token)}
        return headers

    def _make_api_request(self, method, api_service="/search", **kwargs):
        if api_service.startswith("http"):
            url = api_service
        elif api_service.startswith("/"):
            url = self.api_url + api_service
        else:
            url = "{}/{}".format(self.api_url, api_service)
        return requests.request(method, url, **kwargs)

    def get_my_annotations(self):
        return self._make_api_request('GET', api_service='/search', params={'user': self._get_username()})

    def delete_by_id(self, annotation_id):
        headers = self._authorize()
        return self._make_api_request('DELETE', api_service='/annotations/{}'.format(annotation_id), headers=headers)

    def create_annotation(self, target, text, uri, group='Kzwy6GDV', tags=[]):
        headers = self._authorize()
        new_annotation = self._get_new_annotation_params(target, text, uri, group, tags)
        return self._make_api_request('POST', api_service='/annotations', json=new_annotation, headers=headers)

        
def test(args):
    logger.setLevel(logging.DEBUG)
    logger.debug('debug mode is on')
    sys.path.append('..')
    from dotenv import load_dotenv
    load_dotenv('../.env')
    from app import create_app
    app = create_app('development')
    ctx = app.app_context()
    ctx.push()
    bot = AnnotatorBot(ctx, 'AnnotatorBot1')

    # # DELETE
    # id_to_delete = "sE0VrKulEeiw5s-amz7n-w"
    # r = bot.delete_by_id(id_to_delete)
    # print(r)
    # print(r.json())

    # CREATE
    # uri = "http://localhost:5050/chp/histories/1"
    # with open('/home/jporteno/code/science_history_institute/testtextquoteselector.json', 'r') as f:
    #     j = json.load(f)
    # r = bot.create_annotation(j, 'a second annotation at the end of the document', uri, tags=['autotag', 'autotag2'])
    # print(r)
    # print(r.json())
    # print()

    annotation_id = "jAKRAK05Eeiw5rO44INx4g"
    r = bot._make_api_request('PATCH', api_service="/annotations/{}".format(annotation_id), json={"hidden": True})
    print(r)
    print(r.json())
    print()

    r = bot.get_my_annotations()
    j = r.json()
    rows = j['rows']
    for row in rows:
        print(row['id'], row['text'])
        # for k, v in row.items():
        #     if k != "target":
        #         print(k, v)

    ctx.pop()

def main(args):
    if args.test:
        test(args)

if __name__ == "__main__":
    total_start = timer()
    logger = logging.getLogger(__name__)
    logger.info(" ".join(sys.argv))
    logger.info( '{:%Y-%m-%d %H:%M:%S}'.format(datetime.now()) )
    import argparse
    parser = argparse.ArgumentParser(description="TODO: description")
    parser.add_argument("--test", action='store_true', help="run test function")
    parser.add_argument("--debug", action='store_true', help="output debugging info")
    global args
    args = parser.parse_args()
    if args.debug:
        logger.setLevel(logging.DEBUG)
        logger.debug('debug mode is on')
    else:
        logger.setLevel(logging.INFO)
    main(args)
    total_end = timer()
    logger.info('all finished. total time: {}'.format(format_timespan(total_end-total_start)))
