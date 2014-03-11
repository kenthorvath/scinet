#!/usr/bin/python2.7

import sys, getopt #for command line arguments
from Bio import Entrez as pm
import networkx as nx
import matplotlib.pyplot as plt

def main(argv):

  #Initial Configuration
  
  email = "email@example.net"
  searchField = "Telomeres"
  maxResults = 100

  #Command Line Option Parsing

  try:
    opts, args = getopt.getopt(argv,"hq:e:n:",["query=","email=","number="])
  except getopt.GetoptError:
    print 'scinet.py -q <query> -e <your@email> -n <number>'
    sys.exit(2)

  for opt, arg in opts:
    if opt == '-h':
      print 'scinet.py -q <query> -e <your@email> -n <number>'
      sys.exit()
    elif opt in ("-q", "--query"):
      searchField = arg
    elif opt in ("-e", "--email"):
      email = arg
    elif opt in ("-n", "--number"):
      maxResults = arg


  #Configure Entrez email, per requirement
  pm.email = email

  #Construct an empty graph G, which represents the coauthorship of researchers in the telomere field
  G = nx.MultiGraph()

  #Get a list of the most recent articles in the specified field
  # field = " ".join(argv) if argv else "telomere"
  print "Analyzing field %s" % searchField
  results = pm.read(pm.esearch(db='pubmed', term=searchField, retmax=maxResults))['IdList']
  records = pm.parse(pm.efetch(db="pubmed", id=",".join(results), retmode="xml"))

  print "Retrieved list of articles"

  #For each article in the list, get a list of the articles authors

  for record in records:
    try:
      authorList = record['MedlineCitation']['Article']['AuthorList']
      articleTitle = record['MedlineCitation']['Article']['ArticleTitle'].encode("ascii", "ignore")
    except KeyError:
      pass
    
    #For each possible pair of coauthors in this list,
    #add an edge to graph G such that the edge contains the article's 
    #title, journal, and pubmed_id, and retraction status
    
    try:
      for author1 in authorList:
        authorID1 = author1['LastName'] + ", " + author1['ForeName'].split()[0] 
        for author2 in authorList:
          authorID2 = author2['LastName'] + ", " + author2['ForeName'].split()[0] 
          if (authorID1 != authorID2) and not G.has_edge(authorID1,authorID2): G.add_edge(authorID1, authorID2, title=articleTitle) 
    except KeyError:
      pass
  print "Network topology complete"

  #visualize the graph G
  nx.draw_graphviz(G)
  plt.show()

  #Find the cliques in G, which represent collaborative groups of researchers.

  #Rank the 'proliferativity' of a given researcher based on the number of edges

  #Rank the 'integrity' of a given researcher based on the number of edges containing a retraction flag

  #Rank the 'suspicion index' of a given researcher as a composite average of the integrity of adjacent researchers

if __name__ == "__main__":
  main(sys.argv[1:])
