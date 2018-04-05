"""
extract information from fandom.wikia
"""

import json
import requests
from pprint import pprint

def getArticleInfo(domain,id):
    url = "http://{0}.wikia.com/api/v1/Articles/Details/?ids={1}&abstract=500".format(domain,id)
    r = requests.get(url)
    info = {'title':'title','abstract':'abstract','thumbnail':False}
    js = r.json()
    try:
        info['title'] = js['items'][str(id)]['title']
        info['abstract'] = js['items'][str(id)]['abstract']
        info['thumbnail'] = js['items'][str(id)]['thumbnail']
        return info
    except:
        return info
        
        

def search_char(domain,name):
    name = name.replace(' ', '+')
    url = "http://{0}.wikia.com/api/v1/Search/List/?query={1}&limit=2".format(domain,name)
    r = requests.get(url)
    try:
        id = r.json()['items'][0]['id']
        return getArticleInfo(domain, id)
    except:
        return {'title':'title','abstract':'abstract','thumbnail':False}


def name2json(domain,names,fname):
    """
    Takes list of names - people names
    domain - fandom.wiki domain for names
    fname - output filename

    Extracts information from fandom pages
    """
    items = {}
    for name in names: 
        items[name] = search_char(domain,name)
        pprint(items[name])
    json.dump(items,open(fname,'w'))

