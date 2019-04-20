from flask import Flask, render_template, request, redirect, url_for

from nltk.corpus import wordnet as wn
from textblob import TextBlob

import re
import json

import requests
from bs4 import BeautifulSoup

from random import randint

import pysolr

def solr_api(ip_addr, port, search_text, coreName):

    solr_addr = 'http://' + ip_addr + ':' + port + '/solr/' + coreName + '/'
    solr = pysolr.Solr(solr_addr, timeout=10)

    results = solr.search('title:'+search_text)

    for result in results:
        print("The title is '{0}'.".format(result['text']))

if __name__ == '__main__':

    ip_addr = '34.83.164.119'
    port = '8983'
    doc_id = 'Anarchism'
    core_name = 'wiki_dev'
    solr_api(ip_addr, port, doc_id, core_name)

    # print(doc_body)
    # print(len(doc_body))
    # print(doc_url)
    # print(len(doc_url))