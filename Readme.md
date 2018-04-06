Social Groups in Novels
=======================

Often novels contain numerous characters that frequently associate with others forming groups. This project focuses on identifying these social groups. Social groups may be people belonging to the same family, tribe, profession, close friends etc. Results uploaded into this repository mainly focuses on the Harry Potter series so, some of the groups identified involve groups like:
- Quidditch players
- Weasley Family members
- Professors at Hogwarts
- Centaurs
- etc.

This project focuses on only projecting the characters on a two dimensional plane to recognize clusters visually. Naming the clusters as mentioned above in the list is not possible. Here is one such projection:
![](https://s31.postimg.org/h9psx4giz/hp1.png)

More such results can be found in [imgs folder](https://github.com/alella/social_groups/tree/master/imgs). Apart from producing static image files, the code can also produce interactive plots with more character information like below:
![](https://s31.postimg.org/dwhkann0r/scrot_VV0e9.png)

More such interactive plots (html pages) can be found in [plots folder](https://github.com/alella/social_groups/tree/master/plots). The following shows a human annotated version of the results:
![](https://s31.postimg.org/b8s40gmbf/scroti_K25_G.png)

Instructions to generate graphs
===============================

1. Clone repository and install dependencies
```
git clone "https://github.com/alella/social_groups.git"
pip install -r requirements.txt
```

2. Pick a novel and convert it into a txt file. Say you have 'Harry Potter and the Chamber of secrets.epub', you need to convert it to a txt file and rename it as 'b_harrypotterbook2.txt'. It is mandatory to include 'b_' at the begining of the filename and end the filename with '.txt'.

3. Once you have the txt file, you can extract information required to draw the plots by running:
```
python book2nouns.py /path/to/b_harrypotterbook2.txt
```
This step would take somewhere between 10 to 20 hrs depending upon how big the book is. Once this is done, you no longer need to extract information from the book any more. 

4. Now, you should have extracted book's information stored in `extracts`, `cooccurances` folders. To plot the graphs run:
```
python plot_people.py harrypotterbook2 harrypotter
```
Format for `plot_people.py` is - `python plot_people.py <book_name> <fandom.wiki_domain>`. Where `<book_name>` is name of the book without complete path and without 'b_' prefix and '.txt' suffix. `<fandom.wiki_domain>` is the name of the subdomain from fandom wiki pages. For harry potter the fandom wiki page is http://harrypotter.wikia.com . So, the subdomain is `harrypotter`. This second argument is required for displaying character information in interactive plots. If fandom pages do not exists for your book, then interactive plots cannot be produced but, the script would still produce static images.

Algorithm/Procedure
===================

The main idea involves using Stanford's NER Tagger to extract names in each line of the text and building a feature vector by observing other entities or nouns surrounding this name within a fixed window of words. A feature vector is generated for each person in the novel that appear more than a set minimum threshold. This vector is generated by looking at most frequently occuring entities around the person. Depending upon the parameters specified the length of the vector ranges from 200 to 500. Its hard to visualize a high dimensional vector so, this gets projected to a two dimensional surface using t-SNE (t-Distributed Stochastic Neighbor Embedding).