import json
import re, string
import matplotlib.pyplot as plt
from collections import defaultdict
from ibm_watson import ToneAnalyzerV3
from ibm_cloud_sdk_core.authenticators import IAMAuthenticator
from nltk.corpus import stopwords
from nltk.tokenize import TweetTokenizer
from nltk.tag import pos_tag
from nltk.stem.wordnet import WordNetLemmatizer
from sklearn.feature_extraction.text import CountVectorizer
from sklearn.decomposition import LatentDirichletAllocation

tokenizer = TweetTokenizer()
stop_words = stopwords.words('english')
#keep words that may contribute to sentiment 
stop_words.pop(stop_words.index('no'))
stop_words.pop(stop_words.index('not'))
stop_words.pop(stop_words.index('against'))
stop_words.pop(stop_words.index("couldn't"))
stop_words.pop(stop_words.index("aren't"))
stop_words.pop(stop_words.index("won't"))
            
def read_jsonl(filename):
    '''Iterates through a JSONL file'''
    with open(filename, "r", encoding="utf8") as f:
        for line in f:
            yield json.loads(line.rstrip('\n|\r'))
            

def remove_noise(tweet_tokens, stop_words = ()):
    '''
    Cleans the tweet tokens, removing links and special characters,
    tags part of speech of words, and lemmatizes
    '''
    cleaned_tokens = []

    for token, tag in pos_tag(tweet_tokens):
        token = re.sub('http[s]?://(?:[a-zA-Z]|[0-9]|[$-_@.&+#]|[!*\(\),]|'\
                       '(?:%[0-9a-fA-F][0-9a-fA-F]))+','', token)
        token = re.sub("(@[A-Za-z0-9_]+)","", token)

        if tag.startswith("NN"):
            pos = 'n'
        elif tag.startswith('VB'):
            pos = 'v'
        else:
            pos = 'a'

        lemmatizer = WordNetLemmatizer()
        token = lemmatizer.lemmatize(token, pos)

        if len(token) > 0 and token not in string.punctuation and token.lower() not in stop_words:
            cleaned_tokens.append(token.lower())
    return cleaned_tokens


# Initialize IBM Tone Analyzer
authenticator = IAMAuthenticator('oOr5wTdWVlT_Hd5MN5KOP1EioQ-RKQybSJi4opODtaPD')
tone_analyzer = ToneAnalyzerV3(
    version='2017-09-21',
    authenticator=authenticator
)
tone_analyzer.set_service_url('https://api.us-east.tone-analyzer.watson.cloud.ibm.com')

### Reading tweet data from json file
datareader = read_jsonl('../json/candidate-tweets/democratic-candidate-timelines.jsonl')

tweet_by_user = defaultdict(list)
tone_by_user = defaultdict(list)
count = 0
for tweet in datareader:
    # Break for loop early, for testing purposes
    count += 1
    print(count)
    # Read in data and preprocess
    text = tweet['full_text']
    name = tweet['user']['name']
    tokenized_tweet = tokenizer.tokenize(text)
    cleaned_text = remove_noise(tokenized_tweet, stop_words)
    tweet_by_user[name].append(' '.join(cleaned_text))
    
    #Tone analysis
    if not text:
        continue
    tone_analysis = tone_analyzer.tone(
        {'text': text},
        content_type='application/json',
        sentences = False
    ).get_result()
    tone_by_user[name].append(tone_analysis['document_tone'])
    
### TESTING TONE ANALYSIS ###
# Generate bar graph of tone distributions
for user in tone_by_user:
    tone_dict = defaultdict(float)
    for tone_analysis in tone_by_user[user]:
        for tone in tone_analysis['tones']:
            tone_dict[tone['tone_name']] += tone['score']
    
    plt.figure()
    plt.title(f"{user}'s Twitter Tone Distribution")
    plt.bar(*zip(*tone_dict.items()))
    plt.show()
    
### TESTING TOPIC MODELING (LDA) ###
vectorizer = CountVectorizer(max_df=0.9, min_df=5, token_pattern='\w+|\$[\d\.]+|\S+')

# Here we use Bernie Sanders' tweets as an example
tf = vectorizer.fit_transform(tweet_by_user['Bernie Sanders']).toarray()
tf_feature_names = vectorizer.get_feature_names()
# topic model
model = LatentDirichletAllocation(n_components=6, random_state=0)
model.fit(tf)

def display_topics(model, feature_names, no_top_words):
    topic_dict = {}
    for topic_idx, topic in enumerate(model.components_):
        topic_dict["Topic %d words" % (topic_idx)]= ['{}'.format(feature_names[i])
                        for i in topic.argsort()[:-no_top_words - 1:-1]]
        topic_dict["Topic %d weights" % (topic_idx)]= ['{:.1f}'.format(topic[i])
                        for i in topic.argsort()[:-no_top_words - 1:-1]]
    return topic_dict

top_dict = display_topics(model, tf_feature_names, 8)
