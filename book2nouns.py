"""
Converts given book (b_bookname.txt) into 2 files:
linext_bookname.json : Contains names and other nouns, entities extracted for each line
co_bookname.json: Contains a list of names that co occur, wrt book's chronological order.

Usage: python books2nouns.py /path/to/b_bookname.txt
"""

import os
import sys
import json
import nltk
import urllib
import zipfile

from pprint import pprint
from hashlib import md5
from nltk.tag.stanford import StanfordNERTagger as NERTagger

def ner_tagger():
    """
    Checks if libraries exists. If not, downloads them.
    Returns NERTagger object
    """
    # Download Stanford-NER if it does not exists
    if not os.path.exists('ner.zip'):
        download_url = "https://nlp.stanford.edu/software/stanford-ner-2018-02-27.zip"
        print "Downloading ", download_url, "as ner.zip"
        urllib.urlretrieve("https://nlp.stanford.edu/software/stanford-ner-2018-02-27.zip","ner.zip")
    # Extract Stanford-NER library
    if not os.path.exists('./stanford-ner'):
        zip_ref = zipfile.ZipFile("ner.zip", 'r')
        zip_ref.extractall()
        zip_ref.close()
        os.rename('./stanford-ner-2018-02-27', './stanford-ner')
        
    st = NERTagger('./stanford-ner/classifiers/english.all.3class.distsim.crf.ser.gz',
                   './stanford-ner/stanford-ner.jar')
    return st
 
def asciify(text):
    """
    filters out non alphanumeric characters from text
    """
    
    return ''.join([i if ord(i) < 128 else ' ' for i in text])

def print_in_line(content):
    """
    Prints without a new line i.e, overrites output buffer
    """
    
    sys.stdout.write("\r"+str(str(content)+"                  "))
    sys.stdout.flush()

def extract_people_and_ents(line, st, name_map, ents_map, coccuer):
    """
    Example 1:
    -------
    line   : I have one myself above my left knee that is a perfect map of the London Underground.
    output : {'ents': [u'London', u'Underground'], 'people': []}
    
    Example 2:
    -------
    line   : But I c-c-can't stand it. Lily an James dead an poor little Harry off ter
             live with Muggles. Yes, yes, it's all very sad, but get a grip on yourself,
             Hagrid, or we'll be found, Professor McGonagall whispered, patting Hagrid
             gingerly on the arm as Dumbledore stepped over the low garden wall and
             walked to the front door.

    output : {'ents': [],
              'people': [u'Lily', u'James', u'Hagrid',
                         u'McGonagall', u'Hagrid', u'Dumbledore']}
    """
    words = nltk.word_tokenize(line)
    people = [x[0] for x in st.tag(words) if x[1]=='PERSON']
    ents = [x[0] for x in st.tag(words) if x[1]!='PERSON' and x[1]!='O']
    people_indices = [words.index(t) for t in people]
    ents_indices = [words.index(t) for t in ents]
    toremove=[]

    # Normalize people
    for i,idx in enumerate(people_indices):
        if idx+1 in people_indices:
            try:
                coccuer.append((people[i],people[i+1]))
            except:
                pass

    for name in toremove:
        people.remove(name)
    people = [name_map.get(t,t) for t in people]
    toremove=[]


    for name in toremove:
        ents.remove(name)
    ents = [ents_map.get(t,t) for t in ents]
    out = { "people":people, "ents":ents}
    
    return out

def extract_nouns(line):
    """
    extract all nouns from line

    Example:
    line   : He got into his car and backed out of number four drive.
    output : ['car', 'number', 'drive']
    """

    words = nltk.word_tokenize(line)
    pos = nltk.pos_tag(words)
    nouns = []
    for el in pos:
        word,form = el
        if form.startswith('NN'):
            if word.endswith('s'):
                word = word[:-1]
            nouns.append(word)

    return nouns

def line2words(line, st, name_map, ents_map, coccuer,no=0):
    """
    Example output:
    --------------
    {'ents': [],
     'line': 'Mrs. Dursley was thin and blonde and had nearly twice the
             usual amount of neck, which came in very useful as she spent
             so much of her time craning over garden fences, spying on the
             neighbors.',
     'no': 0,
     'nouns': ['Mrs.', 'Dursley', 'blonde',
               'amount','neck', 'time',
               'craning','garden','fence','neighbor'],
     'people': [u'Dursley']}
    }
    """
    
    pns = extract_people_and_ents(line, st, name_map, ents_map, coccuer)
    out = {
        "no": no,
        "people": pns["people"],
        "ents": pns["ents"],
        "nouns": extract_nouns(line),
        "line":line
    }
    
    return out


def process_book(fn_book):
    fn_book_base = os.path.basename(fn_book)
    if not fn_book_base.startswith('b_'):
        print "Book has to start with b_ and of txt format"
    if not fn_book_base.endswith('.txt'):
        print "Book has to end with .txt and of txt format"

    book = fn_book_base[2:].split('.')[0]
    fn_extract = 'extracts/{0}.json'.format(book)
    fn_cooccer = 'cooccurrances/{0}.json'.format(book)
    name_map = {}
    ents_map = {}
    coccuer = []
    st = ner_tagger()
    with open(fn_book) as f:
        book = f.read()
        book = asciify(book)
        lines = nltk.sent_tokenize(book) 
        c=0 
        line_extracts={}
        line_list={}
        for line in lines:
            c+=1
            print_in_line("Line {0} of {1} -- {2:.3f}% ".format(c,len(lines), c*100.0/len(lines)))
            lhash = md5(line).hexdigest()
            line_list[c] = line
            ext = line2words(line, st, name_map, ents_map, coccuer, no=c)
            line_extracts[lhash] = ext
            if c%100==0:
                json.dump(line_extracts, open(fn_extract,'w'))
                json.dump(coccuer, open(fn_cooccer,'w'))
                break

    json.dump(line_extracts, open(fn_extract,'w'))

if __name__=='__main__':
    args = sys.argv
    print args
    if len(args)!=2:
        print "Missing args: python line_extract.py /path/to/book.txt"
    process_book(args[1])
