
## Output will be new CSV file that includes Sentiment Score and Sentiment for each review in scraped HP Printer product reviews ##
## Sentiment for each review will be one of "positive", "negative" or "neutral" ##

## Import statements for functions in Funcs_Sentiment ##
import pandas as pd
from Funcs_Sentiment import remove_stopwords
from Funcs_Sentiment import transform_neg
from Funcs_Sentiment import POS_tagger
from Funcs_Sentiment import get_wordnet_pos
from Funcs_Sentiment import lemmatize_words
from Funcs_Sentiment import sentiment_dict
from Funcs_Sentiment import sentiment_score
from Funcs_Sentiment import sentiment_class


# Read in files (saved locally to same folder as this python file)
printers = pd.read_csv("FlipKart_Printers.csv")
laptops = pd.read_csv("FlipKart_Notebooks.csv")
tablets = pd.read_csv("FlipKart_Tablets.csv")


# Initialize stopwords list, lemmatizer, both tokenizers
stop = stopwords.words("english")
lmtzr = WordNetLemmatizer()
word_tokenizer = SpaceTokenizer()
punc_tokenizer = RegexpTokenizer('\w+')

# Clean Text --> 1) Lowercase, 2) Tokenize for stopword removal, 
# 3) Remove stopwords, 4) Re-join tokenized list
printers['Reviews'] = printers['Reviews'].str.lower()
printers['Reviews'] = printers['Reviews'].apply(word_tokenizer.tokenize)
printers['Reviews'] = printers['Reviews'].apply(remove_stopwords)
printers['Reviews'] = printers['Reviews'].apply(" ".join)


## Apply functions for text processing using Pandas apply for efficiency ##
## Creating new columns in dataframe containing results to identify any mistakes as they occur ##

printers['Transformed Reviews'] = printers['Reviews'].apply(transform_neg)
printers['Transformed Reviews'] = printers['Transformed Reviews'].apply(punc_tokenizer.tokenize)

# Part of Speech Tagging ~ 1 min for 1100 reviews --> Most time consuming portion of text processing
printers['POS'] = printers['Transformed Reviews'].apply(POS_tagger)
printers['Lemmatized Reviews']= printers['POS'].apply(lemmatize_words)

# Create final column for joined PROCESSED reviews
printers['Processed Reviews'] = printers['Lemmatized Reviews'].apply(" ".join)

# Open sentiment dictionary file, calculate sentiment scores and classify them
sentiment = sentiment_dict("SentiStrengthDictionary.csv")
printers['Sentiment Score'] = printers['Lemmatized Reviews'].apply(sentiment_score)


# Create new dataframe to contain columns desired in CSV output
printers_senti_df = pd.DataFrame(printers, columns=['Dates','Products','Ratings','Processed Reviews','Sentiment Score'])

# Assign "positive", "negative" or "neutral" to scores
printers_senti_df['Sentiment'] = printers_senti_df['Sentiment Score'].apply(sentiment_class)

# Write final dataframe to CSV
printers_senti_df.to_csv("HP_Printers_Sentiment.csv")