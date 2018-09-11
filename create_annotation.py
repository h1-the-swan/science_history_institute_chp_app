import os

def create_new_annotation(target, text, uri, group='Kzwy6GDV', tags=[]):
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

def get_token_params(app, username):
    token = app.hypothesis_client.grant_token(username=username)
    params = {
        'assertion': token.decode(),
        'grant_type': 'urn:ietf:params:oauth:grant-type:jwt-bearer',
    }
    return params
