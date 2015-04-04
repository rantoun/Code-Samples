## Function definitions to be used to prepare text for sentiment analysis and to assign scores/sentiment to text ##
## Import statements and required packages ##

import pandas as pd
import re
import nltk
from nltk.tokenize import SpaceTokenizer
from nltk.tokenize import RegexpTokenizer
from nltk.corpus import stopwords
from nltk.corpus import wordnet
from nltk.stem.wordnet import WordNetLemmatizer


''' 

    Text Processing includes:
        1. Stopword Removal --> remove high frequency words with little meaning ("I","you","the",etc.)
        2. Prepend "NEG_" to certain words --> improves sentiment accuracy in regards to subtleties in text
            - specifically related to positive words used with a negative light
            - i.e. "not great at scanning." will become "not NEG_great NEG_at NEG_scanning"
        3. Part-of-Speech Tagging
        4. Lemmatization --> reduce word to its lemma or root
            - i.e. "walking" --> "walk" ; "came" --> "come"
            - done to increase matches to words in sentiment dictionary
        5. Tokenization --> splitting reviews into individual words and removal of punctuation marks


'''

# Remove stopwords except for "not" and "no" to maintain for transform_neg function
def remove_stopwords(x):
    new_x = []
    for word in x:
        if word == "not" or word == "no":
            new_x.append(word)
        elif word not in stop:
            new_x.append(word)
    return new_x

# Prepend "NEG_" to words following "not", "never", etc. until the next punctuation mark
def transform_neg(x):
    transformed = re.sub(r'\b(?:not|never|no|n\'t|n\\\'t|nt|cannot|con|cons)\b[\w\s]+[^\w\s]', 
       lambda match: re.sub(r'(\s+)(\w+)', r'\1NEG_\2', match.group(0)), 
       x,
       flags=re.IGNORECASE)
    return transformed

# Part of speech tagging using NLTK
def POS_tagger(x):
    pos = nltk.pos_tag(x)
    pos = [list(tup) for tup in pos]
    return pos

# Translate POS-tag to wordnet form for accurate lemmatization
def get_wordnet_pos(treebank_tag):
    if treebank_tag.startswith('J'):
        return wordnet.ADJ
    elif treebank_tag.startswith('V'):
        return wordnet.VERB
    elif treebank_tag.startswith('N'):
        return wordnet.NOUN
    elif treebank_tag.startswith('R'):
        return wordnet.ADV
    else:
        return wordnet.ADV

# Lemmatization    
def lemmatize_words(x):
    lemmatized = []
    for i in range(len(x)):
        lemmatized.append(str(lmtzr.lemmatize(x[i][0],get_wordnet_pos(x[i][1]))))
    return lemmatized

# Read in and clean pre-built sentiment dictionary with words and associated scores
# Scores between -5 (most negative) and +5 (most positive)
def sentiment_dict(sentimentData):
    '''
        SentiStrength emotion lookup table in dictionary form
        Takes file as .csv with 2 columns ("Words","Sentiment Score")
    '''
    f = pd.read_csv(sentimentData)
    f['Words'] = f['Words'].str.replace(r'*','')

    f_sentiment = f.drop_duplicates(cols='Words', take_last=True)
    f_sentiment = f_sentiment.reset_index()
    del f_sentiment['index']

    senti_dict = f_sentiment.set_index('Words')['Sentiment Score'].to_dict()
    return senti_dict

# Score each review based on words in review matching to those found in sentiment dictionary
def sentiment_score(x):
    ''' x should be a list of tokenized reviews '''
    # take note of location of "SentiStrengthDictionary.csv"
    review = x

    # Change path to location of SentiStrengthDictionary.csv
    sentiment = sentiment_dict("./SentiStrengthDictionary.csv")
    sent_score = 0
    
    for word in review:
        if not (word == ""):
            if word.startswith('NEG_'):
                sent_score += -0.5
            elif word in sentiment.keys():
                sent_score += float(sentiment[word])
    
    return sent_score

# Classify sentiment based on criteria below
def sentiment_class(x):
    if x <= -2:
        sentiment = "negative"
    elif x >= 2:
        sentiment = "positive"
    else:
        sentiment = "neutral"
    return sentiment

