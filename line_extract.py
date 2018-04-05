from hashlib import md5
import json
import sys
import nltk
from pprint import pprint
from nltk.tag.stanford import StanfordNERTagger as NERTagger
# st = NERTagger('/scratch/avl160230/bitbucket/threat/stanford-ner/classifiers/english.all.3class.distsim.crf.ser.gz', '/scratch/avl160230/bitbucket/threat/stanford-ner/stanford-ner.jar')
st = NERTagger('/home/ozz/bitbucket/holmes/stanford-ner/classifiers/english.all.3class.distsim.crf.ser.gz', '/home/ozz/bitbucket/holmes/stanford-ner/stanford-ner.jar')
name_map = {}
ents_map = {}
coccuer = []

def asciify(text):
    return ''.join([i if ord(i) < 128 else ' ' for i in text])


def extract_people_and_ents(line):
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
    #         if people[i] not in name_map:
    #             name_map[people[i]] = "{0} {1}".format(people[i], people[i+1])
    #             name_map[people[i+1]] = "{0} {1}".format(people[i], people[i+1])
    #         try:
    #             toremove.append(people[i+1])
    #         except:
    #             pass

    for name in toremove:
        people.remove(name)
    people = [name_map.get(t,t) for t in people]
    # print people_indices
    # print name_map
    # print people
    toremove=[]

    # Normalize ents
    # for i,idx in enumerate(ents_indices):
    #     if idx+1 in ents_indices:
    #         if ents[i] not in ents_map:
    #             ents_map[ents[i]] = "{0} {1}".format(ents[i], ents[i+1])
    #         toremove.append(ents[i+1])

    for name in toremove:
        ents.remove(name)
    ents = [ents_map.get(t,t) for t in ents]
    # print ents_indices
    # print ents_map
    # print ents
    
    return { "people":people, "ents":ents}

def extract_nouns(line):
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

def line2words(line,no=0):
    """
    Extracts line to :{
      "no": 1,
      "people":
      "ents":
      "nouns":
      "line":
    }
    """
    pns = extract_people_and_ents(line)
    out = {
        "no": no,
        "people": pns["people"],
        "ents": pns["ents"],
        "nouns": extract_nouns(line),
        "line":line
    }
    return out

# extract_people_and_ents("Mr. Dursley, of number four, Privet Drive, were proud to say that they were perfectly normal, thank you very much.")
# pprint(line2words("Uncle Vernon stayed at home again. After burning all the letters, he got out a hammer and nails and boarded up the cracks around the front and back doors so no one could go out. He hummed Tiptoe Through the Tulips as he worked, and jumped at small noises."))
# pprint(line2words("Mr. Dursley, of number four, Privet Drive, were proud to say that they were perfectly normal, thank you very much."))


with open('b_lotr1.txt') as f:
    book = f.read()
    book = asciify(book)
    lines = nltk.sent_tokenize(book) 
    c=0 
    line_extracts={}
    line_list={}
    for line in lines:
        c+=1
        print c,len(lines)
        lhash = md5(line).hexdigest()
        line_list[c] = line
        ext = line2words(line)
        line_extracts[lhash] = ext
        if c%100==0:
            json.dump(line_extracts, open('linext.json','w'))
            json.dump(coccuer, open('coccuer.json','w'))
            print name_map

#pprint(line_extracts)
json.dump(line_extracts, open('linext.json','w'))
json.dump(name_map, open('name_map.json','w'))
