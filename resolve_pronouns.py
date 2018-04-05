"""
NOT WORKING ON THIS ANYMORE
"""

import nltk
import sys
from neuralcoref import Coref

coref = Coref()
old_book_name = sys.argv[1]
new_book_name = sys.argv[2]
print "cast {0} to {1}".format(old_book_name, new_book_name)
# context = u"\"We should start back,\" Gared urged as the woods began to grow dark around them. \"The wildlings are dead.\"\n\n\"Do the dead frighten you?\" Ser Waymar Royce asked with just the hint of a smile.\n\nGared did not rise to the bait. "
# utterances = u"He was an old man, past fifty, and he had seen the lordlings come and go."

def asciify(text):
    return ''.join([i if ord(i) < 128 else ' ' for i in text])

def has_personal_pronouns(line):
    pros = ['he', 'she', 'him', 'her']
    for p in pros:
        if p in line.lower():
            return True
    return False

with open(old_book_name) as f:
    book = asciify(f.read().replace('\r', ''))
    sentences = nltk.sent_tokenize(book) 

c=0
newbook = ""
name = ""
for i, utter in enumerate(sentences):
    if i<20:
        continue
    if has_personal_pronouns(utter):
        context = unicode(" ".join(sentences[i-4:i-1]))
        # print "--"*10
        # print "context"
        # print context
        # print "utter: ", utter
        coref.one_shot_coref(utterances=unicode(utter), context=context)
        res = coref.get_resolved_utterances()[0]
        dreps = coref.get_most_representative()
        for k,v in dreps.iteritems():
            k = str(k)
            v = str(v)
            if v.lower() in res:
                res = res.replace(v.lower(), v)
                name = v
        # print "res: ", res
        c+=1
        newbook+=" "+res
    else:
        newbook+=" "+utter

    per = i*100.0/len(sentences)
    print "{0:.2f}% {1}".format(per, name)

with open(new_book_name, 'w') as w:
    w.write(newbook)
 
 
