"""
plot data from <book> using <story_domain>'s fandom.wikia

TODO: Try Lord of the Rings.
"""
import os
import webbrowser
from sklearn.manifold import TSNE
from sklearn.decomposition.pca import PCA
from collections import Counter
import numpy as np
from collections import Counter
from pprint import pprint
import json
from sklearn.feature_extraction.text import TfidfVectorizer
import sys

import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
import matplotlib.cm as cm

st_color = '#505050'
# plt.style.use(['dark_background'])
# facecolor= "#000000"
facecolor= "#ffffff"
matplotlib.rc('axes',edgecolor=facecolor)
matplotlib.rc('xtick',color=facecolor)
matplotlib.rc('ytick',color=facecolor) 
matplotlib.rc('lines', linewidth=1)
matplotlib.rc('text', color="#000000")
matplotlib.rc('font', size=7)

book="lotr1"
story_domain="lotr"
cooccur='co_'+book+'.json'
linext = 'linext_'+book+'.json'

# Normalize names
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
        
print "\n".join(nnames.values())


linext = json.load(open(linext))
# all_names = [t['people'] for t in linext.values()]
# all_names = list(set([item for sublist in all_names for item in sublist]))
# non_people += [t+'s' for t in all_names]
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
        assocs[person] = assocs.get(person,[]) + [[t.lower() for t in nouns]]
        # assocs[person] = assocs.get(person,[]) + [[t.lower() for t in people]]
        ents[person] = line['ents']
        namecnt[person] = namecnt.get(person, 0)+1


# Build features
main_char = sorted(namecnt.iteritems(), key=lambda x:-x[1])[0][0]
features = []
fsize=10
person_mincount = 7
ksize=5
for person in assocs.keys():
    if namecnt[person]<person_mincount:
        continue
    # print person, namecnt[person]
    an=[]
    # X = [" ".join(item) for item in assocs[person]]
    for item in assocs[person]:
        an+=item
    # tfidf = TfidfVectorizer(max_features=10)
    # tfidf.fit(X)
    # print "tfidf=", tfidf.vocabulary_.keys()
    # if person=='Ember' or person=='Popper':
    #     print "count=",[x for x in Counter(an).most_common(10)]
    # print "ents =", ents[person]
    # print "--"*20
    features += [x[0] for x in Counter(an).most_common(fsize)]
    features += ents[person]


def p2vec(person,fd):
    an=[]
    for item in assocs[person]:
        an+=item
    words = [t for t in Counter(an).most_common(fsize)]
    mc = max([t[1] for t in Counter(an).most_common(fsize)])
    x = np.zeros(len(fd))
    for w,c in words:
        x[fd[w]] = 1
    return x

def prcl(people,preds):
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


from sklearn.cluster import KMeans, AffinityPropagation, AgglomerativeClustering
# kmeans = KMeans(n_clusters=ksize).fit(X)
# print "kmeans"
# prcl(peps,kmeans.labels_)
# print "--"*20

clf = AffinityPropagation()
clf.fit(X)
print "affprop"
prcl(peps,clf.predict(X))
print "--"*20

# clf = AgglomerativeClustering(n_clusters=ksize)
# clf.fit(X)
# print "agg"
# prcl(peps,clf.fit_predict(X))
# print "--"*20
# print X.shape



pca = TSNE(n_components=2,perplexity=5)
#pca = PCA(n_components=2) 
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
plt.savefig('img.png',dpi=200,facecolor=facecolor) 

 


from bokeh.plotting import figure, show, output_file,ColumnDataSource, save 
from bokeh.models import HoverTool

p = figure(tools="hover")
df={'x':[],
    'y':[],
    'name':[],
    'title':[],
    'thumbnail':[],
    'abstract':[]}

if os.path.exists(story_domain+".json"):
    domaininfo = json.load(open(story_domain+".json"))
else:
    from fandom_extract import name2json
    name2json(story_domain, peps)
    domaininfo = json.load(open(story_domain+".json"))
    
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

# output_file("color_scatter.html", title="color_scatter.py example")
# show(p)
save(p)
with open('person_tfidf.html') as f:
    content = f.read()
with open('person_tfidf.html', 'w') as w:
    content = content.replace("<div class=\"bk-root\">", "<div class=\"bk-root\" style=\"margin-top: 180px\">")
    w.write(content)
    
webbrowser.open('person_tfidf.html')
