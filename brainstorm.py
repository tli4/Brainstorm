from flask import Flask, render_template, request, redirect, url_for

from nltk.corpus import wordnet as wn
from textblob import TextBlob

import re
import json

import requests
import pysolr
from bs4 import BeautifulSoup

from random import randint

class Article:
    """Retrieves and analyzes wikipedia articles"""

    def __init__(self, doc_summary, url, title):
        """
        self.page = wikipedia.page(title) 
        """
        self.url = url
        self.title = title
        self.summary = TextBlob(doc_summary)

    def generate_trivia_sentences(self):
        sentences = self.summary.sentences

        # Remove the first sentence - it's never a good one
        del sentences[0]

        trivia_sentences = []
        for sentence in sentences:
            trivia = self.evaluate_sentence(sentence)
            if trivia:
                trivia_sentences.append(trivia)

        return trivia_sentences

    def get_similar_words(self, word):
        # In the absence of a better method, take the first synset
        synsets = wn.synsets(word, pos='n')

        # If there aren't any synsets, return an empty list
        if len(synsets) == 0:
            return []
        else:
            synset = synsets[0]

        similar_words = []
        if len(synset.hypernyms()) > 0:

            # Get the hypernym for this synset (again, take the first)
            hypernym = synset.hypernyms()[0]

            # Get some hyponyms from this hypernym
            hyponyms = hypernym.hyponyms()

            # Take the name of the first lemma for the first 8 hyponyms

            for hyponym in hyponyms:
                similar_word = hyponym.lemmas()[0].name().replace('_', ' ')
                
                if similar_word != word:
                    similar_words.append(similar_word)

                if len(similar_words) == 8:
                    break

        return similar_words

    def evaluate_sentence(self, sentence):
        if sentence.tags[0][1] == 'RB' or len(sentence.words) < 6:
            # This sentence starts with an adverb or is less than five words long
            # and probably won't be a good fit
            return None

        # tag_map = {word.lower(): tag for word, tag in sentence.tags}

        replace_nouns = []
        for word, tag in sentence.tags:
            # For now, only blank out non-proper nouns that don't appear in the article title
            if tag == 'NN' and word not in self.title:
                # Is it in a noun phrase? If so, blank out the last two words in that phrase
                for phrase in sentence.noun_phrases:
                    if phrase[0] == '\'':
                        # If it starts with an apostrophe, ignore it
                        # (this is a weird error that should probably
                        # be handled elsewhere)
                        break

                    if word in phrase:
                        # Blank out the last two words in this phrase
                        [replace_nouns.append(phrase_word) for phrase_word in phrase.split()[-2:]]
                        break

                # If we couldn't find the word in any phrases,
                # replace it on its own
                if len(replace_nouns) == 0:
                    replace_nouns.append(word)
                break
        
        if len(replace_nouns) == 0:
            # Return none if we found no words to replace
            return None

        trivia = {
            'title': self.title,
            'url': self.url,
            'answer': ' '.join(replace_nouns)
        }

        if len(replace_nouns) == 1:
            # If we're only replacing one word, use WordNet to find similar words
            trivia['similar_words'] = self.get_similar_words(replace_nouns[0])
        else:
            # If we're replacing a phrase, don't bother - it's too unlikely to make sense
            trivia['similar_words'] = []

        # Blank out our replace words (only the first occurrence of the word in the sentence)
        replace_phrase = ' '.join(replace_nouns)
        blanks_phrase = ('__________ ' * len(replace_nouns)).strip()

        expression = re.compile(re.escape(replace_phrase), re.IGNORECASE)
        sentence = expression.sub(blanks_phrase, str(sentence), count=1)

        trivia['question'] = sentence
        return trivia

def solr_api(ip_addr, port, coreName, search_id, search_text):
    solr_addr = 'http://' + ip_addr + ':' + port + '/solr/' + coreName + '/'
    solr = pysolr.Solr(solr_addr, timeout=10)
    request = solr.search(search_id + ':' + search_text)
    return request

def generate_trivia(doc, url, title):
    """Generates trivia questions from wikipedia articles. If no
    doc_summary are supplied, pulls from these sample articles:

    'Tony Bennett', 'Gauls', 'Scabbling', 'Henry V, Duke of Carinthia',
    'Ukrainian Women\'s Volleyball Super League'
    """
    # Use the sample articles if the user didn't supply any

    # Retrieve the trivia sentences
    article = Article(doc, url, title)
    questions = article.generate_trivia_sentences()

    trivia_question = []

    for question in questions:
        if len(question['similar_words']) > 3:
            trivia_question = question
            trivia_question['similar_words'] = trivia_question['similar_words'][:3]

    if (trivia_question == []):
        return False

    # Dev: Output to JSON
    # output_file = open("trivia_question.json", 'w')
    # json.dump(trivia_question, output_file, sort_keys=True, indent=4)
    # output_file.close()
    return trivia_question


app = Flask(__name__)

@app.route('/')
@app.route('/index')
def index():
    return render_template('index.html')

@app.route('/game', methods=['GET', 'POST'])
def game():

    if request.method == 'POST':
        ip_addr = '34.83.164.119'
        port = '8983'
        search_text = request.form['search']
        search_id = 'text'
        core_name = 'wiki_dev'
        
        search_results = solr_api(ip_addr, port, core_name, search_id, search_text)

        if (search_results.hits == 0):
            return redirect(url_for('not_found'))

        for result in search_results.docs:
            trivia = generate_trivia(result['text'][0], result['url'][0], result['title'][0])
            if (not trivia == False):
                break

        if (trivia == False):
            return redirect(url_for('not_found'))

        question = trivia["question"]
        selection = trivia["similar_words"]
        answer = trivia["answer"]
        selection.insert(randint(0,3), answer)
        return render_template('game.html', question = question, selection = selection, answer = answer)

@app.route('/correct')
def correct():
    return render_template('correct.html')

@app.route('/wrong')
def wrong():
    return render_template('wrong.html')

@app.route('/not_found')
def not_found():
    return render_template('not_found.html')

if __name__ == '__main__':

    # app.debug = True
    app.run()