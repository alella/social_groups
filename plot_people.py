"""
plot data from <book> using <story_domain>'s fandom.wikia.
If book filename is b_hp1.txt, <book> = hp, <story_domain> = harrypotter
Usage  : python plot_people.py <book> <story_domain>
Example: python plot_people.py hp1 harrypotter

story_domains:harrypotter,themagicians,gameofthrones
"""
import os
import sys
import json
import webbrowser
import numpy as np

from pprint import pprint
from collections import Counter
from sklearn.manifold import TSNE
from sklearn.decomposition.pca import PCA
from sklearn.cluster import AffinityPropagation
from sklearn.feature_extraction.text import TfidfVectorizer

import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
import matplotlib.cm as cm

st_color = '#505050'
facecolor= "#ffffff"
matplotlib.rc('axes',edgecolor=facecolor)
matplotlib.rc('xtick',color=facecolor)
matplotlib.rc('ytick',color=facecolor) 
matplotlib.rc('lines', linewidth=1)
matplotlib.rc('text', color="#000000")
matplotlib.rc('font', size=7)

args = sys.argv
book=args[1]
story_domain=args[2]
fsize=10
person_mincount = 7
perplexity=10
cooccur='cooccurrances/{0}.json'.format(book)
linext = 'extracts/{0}.json'.format(book)
fn_img = 'imgs/{0}.png'.format(book)
fn_plot = 'plots/{0}.html'.format(book)
fn_char_info = 'char_info/{0}.json'.format(book)


# Normalize names
# If first names starts with any mentioned in non_people then, ignore name
# If length firstname or last name < 3 then , ignore name
coc = json.load(open(cooccur))
coc = ["{0} {1}".format(t[0].lower(),t[1].lower()) for t in coc]
non_people = ['Aunt', 'Uncle', 'H.', 'Don', 'Yeh', 'Madam']
removenames=[] 
for c in coc:
    f,l = c.split()
    f=f[0].upper()+f[1:]
    if f in non_people:
        removenames.append(c)
    if len(f)<3 or len(l)<3:
        removenames.append(c)

# Get all names with count > 1
names = [x[0] for x in Counter(coc).iteritems() if x[1]>1]
print "Names before normalization: ", sorted(list(set(names)))
for n in set(removenames):
    if n in names:
        names.remove(n)

nnames={}
lnc={}
for n in names:
    f,l = n.split()
    lnc[l] = lnc.get(l,0) + 1
for n in names:
    f,l = n.split()
    f=f[0].upper()+f[1:]
    l=l[0].upper()+l[1:]
    nnames[f]="{0} {1}".format(f,l)
    if lnc[l.lower()]==1:
        nnames[l]="{0} {1}".format(f,l)

print "Names after normalization: ", sorted(list(set(nnames.values())))


linext = json.load(open(linext))
assocs = {}                     # nouns associated with <person>
ents = {}                       # entities associated with <person>
namecnt = {}                    # no of times <person> appears
non_nouns = []
for line in linext.values():
    people = line['people']
    nouns = [t for t in line['nouns'] if len(t)>=3 and t not in non_nouns]
    for person in people:
        if person in non_people:
            continue
        person = nnames.get(person,person)
        assocs[person] = assocs.get(person,[]) + [t.lower() for t in nouns]
        ents[person] = line['ents']
        namecnt[person] = namecnt.get(person, 0)+1

# Build features
main_char = sorted(namecnt.iteritems(), key=lambda x:-x[1])[0][0]
features = []
ksize=5
for person in assocs.keys():
    if namecnt[person]<person_mincount:
        continue
    features += [x[0] for x in Counter(assocs[person]).most_common(fsize)]
    features += ents[person]
    
print "features from each character =", fsize
print "Minimum person count  =", person_mincount
print "Lenght of feature vector =", len(set(features))


def p2vec(person,fd):
    """
    Convert person to bag of words vector
    """
    an = assocs[person]
    words = [t for t in Counter(an).most_common(fsize)]
    mc = max([t[1] for t in Counter(an).most_common(fsize)])
    x = np.zeros(len(fd))
    for w,c in words:
        x[fd[w]] = 1
    return x

def prcl(people,preds):
    """
    Prints people in each cluster
    """
    K = list(set(preds))
    for k in range(len(K)):
        print [people[i] for i in range(len(people)) if preds[i]==k]
    
    
features = list(set(features))
features = {features[i]:i for i in range(len(features))}
X = np.zeros((1,len(features)))
peps = []
for person in assocs.keys():
    if namecnt[person]<person_mincount:
        continue
    peps.append(person)
    x=p2vec(person,features)
    X = np.vstack((X,x))
X = X[1:]



clf = AffinityPropagation()
clf.fit(X)
print "affprop"
prcl(peps,clf.predict(X))
print "--"*20


pca = TSNE(n_components=2,perplexity=perplexity)
X = pca.fit_transform(X)
print len(peps)
print len(X)
for i,el in enumerate(X):
    x,y = el
    s=peps[i]
    if s==main_char:
        plt.text(x,y,s,fontsize=6,alpha=.6,color='#ff0000')
    else:
        plt.text(x,y,s,fontsize=6,alpha=.6)
    plt.scatter(x,y,s=10,linewidth=0,alpha=1,c='#4286f4')
plt.savefig('img.png',dpi=100,facecolor=facecolor) 
plt.savefig(fn_img,dpi=100,facecolor=facecolor) 

 


from bokeh.plotting import figure, show, output_file,ColumnDataSource, save 
from bokeh.models import HoverTool

p = figure(tools="hover")
df={'x':[],
    'y':[],
    'name':[],
    'title':[],
    'thumbnail':[],
    'abstract':[]}


if os.path.exists(fn_char_info):
    domaininfo = json.load(open(fn_char_info))
else:
    from fandom_extract import name2json
    name2json(story_domain, peps, fn_char_info)
    domaininfo = json.load(open(fn_char_info))
    
for i,el in enumerate(X):
    x,y = el
    s=peps[i]
    df['x'].append(float(x))
    df['y'].append(float(y))
    df['name'].append(s)
    df['title'].append(domaininfo[s]['title'])
    df['thumbnail'].append(domaininfo[s]['thumbnail'])
    df['abstract'].append(domaininfo[s]['abstract'])


df = ColumnDataSource(data=df) 
hover = HoverTool( tooltips="""<div style="margin-top: 0px;"><div><b>@title</b></div><br>
<div>@name</div><br>
<img
    src="@thumbnail" height="200" alt="@imgs" width="200"
    style="margin: 0px 15px 15px 0px;"
></img><br>
<div style="width:200px">@abstract</div></div>
""")
p = figure(tools=[hover], plot_width=1800, plot_height=900) 
p.scatter("x", "y", source=df, fill_alpha=0.6,radius=4,
          line_color=None)

save(p, filename=fn_plot, title=book, resources=None)
with open(fn_plot) as f:
    content = f.read()
with open(fn_plot, 'w') as w:
    content = content.replace("<div class=\"bk-root\">", "<div class=\"bk-root\" style=\"margin-top: 180px\">")
    w.write(content)
    
webbrowser.open(fn_plot)
 
