import codecs
import json
from sklearn.feature_extraction.text import TfidfVectorizer

data_path = 'static/model/intent/data/'
train_list = []


def train_model():
    file_location = data_path + "train_Exit.json"
    file_stream = codecs.open(file_location, 'r', 'utf-8')
    jdata = json.load(file_stream)

    for data in jdata['Exit']:
        train_list.append([data['data'].lower(), 'exit'])

    file_location = data_path + "train_GenerateLyrics.json"
    file_stream = codecs.open(file_location, 'r', 'utf-8')
    jdata = json.load(file_stream)

    for data in jdata['GenerateLyrics']:
        train_list.append([data['data'].lower(), 'generate'])

    file_location = data_path + "train_MatchSong.json"
    file_stream = codecs.open(file_location, 'r', 'utf-8')
    jdata = json.load(file_stream)

    for data in jdata['MatchSong']:
        train_list.append([data['data'].lower(), 'find'])

    file_location = data_path + "train_RecommendSong.json"
    file_stream = codecs.open(file_location, 'r', 'utf-8')
    jdata = json.load(file_stream)

    for data in jdata['RecommendSong']:
        train_list.append([data['data'].lower(), 'recom'])

    file_location = data_path + "train_Greeting.json"
    file_stream = codecs.open(file_location, 'r', 'utf-8')
    jdata = json.load(file_stream)

    for data in jdata['Greeting']:
        train_list.append([data['data'].lower(), 'greet'])

    x_train = [t[0] for t in train_list]
    bigram_vectorizer = TfidfVectorizer(ngram_range=(1, 2), token_pattern=r'\b\w+\b', min_df=1)
    train_bigram_vectors = bigram_vectorizer.fit_transform(x_train)

    return bigram_vectorizer


def intent_classify(intent_model, vectorizer, input_text):
    x_test = [input_text]
    test_bigram_vectors = vectorizer.transform(x_test)
    pred_scm = intent_model.predict(test_bigram_vectors)
    return pred_scm
