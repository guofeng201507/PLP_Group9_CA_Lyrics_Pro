import codecs
import json
import random, re
import pickle
from tqdm import tqdm

SEP = " "  # token separator symbol


def make_ngrams(tokens, N):
    """ Returns a list of N-long ngrams from a list of tokens """

    ngrams = []
    for i in range(len(tokens) - N + 1):
        ngrams.append(tokens[i:i + N])
    return ngrams


def ngram_freqs(ngrams):
    """ Builds dict of TOKEN_SEQUENCEs and NEXT_TOKEN frequencies """

    ### has form TOKEN_SEQUENCE : DICT OF { NEXT_TOKEN : COUNT }
    ###      e.g        "a b c" : {"d" : 4, "e" : 2, "f" : 6 }
    counts = {}

    # Using example of ngram "a b c e" ...
    for ngram in ngrams:
        token_seq = SEP.join(ngram[:-1])  # "a b c"
        last_token = ngram[-1]  # "e"

        # create empty {NEXT_TOKEN : COUNT} dict if token_seq not seen before
        if token_seq not in counts:
            counts[token_seq] = {}

        # initialize count for newly seen next_tokens
        if last_token not in counts[token_seq]:
            counts[token_seq][last_token] = 0

        counts[token_seq][last_token] += 1

    return counts


def next_word(text, N, counts):
    """ Outputs the next word to add by using most recent tokens """

    token_seq = SEP.join(text.split()[-(N - 1):]);
    choices = counts[token_seq].items();

    # make a weighted choice for the next_token
    # [see http://stackoverflow.com/a/3679747/2023516]
    total = sum(weight for choice, weight in choices)
    r = random.uniform(0, total)
    upto = 0
    for choice, weight in choices:
        upto += weight;
        if upto > r: return choice
    assert False  # should not reach here


def preprocess_corpus(filename):
    # s = open(filename, 'r').read()
    s = ''
    import pandas as pd
    df = pd.read_csv(filename)
    for index, row in tqdm(df.iterrows(), total=df.shape[0]):
        s = s + row['text'].replace('\r', '').replace('\n', '')

    s = re.sub('[()]', r'', s)  # remove certain punctuation chars
    s = re.sub('([.-])+', r'\1', s)  # collapse multiples of certain chars
    s = re.sub('([^0-9])([.,!?])([^0-9])', r'\1 \2 \3', s)  # pad sentence punctuation chars with whitespace
    s = ' '.join(s.split()).lower()  # remove extra whitespace (incl. newlines)
    return s


def postprocess_output(s):
    s = re.sub('\\s+([.,!?])\\s*', r'\1 ', s)  # correct whitespace padding around punctuation
    s = s.capitalize()  # capitalize first letter
    s = re.sub('([.!?]\\s+[a-z])', lambda c: c.group(1).upper(), s)  # capitalize letters following terminated sentences
    return s


def gengram_sentence(model, N=3, sentence_count=15, start_seq=None):
    """ Generate a random sentence based on input text corpus """

    counts = model

    if start_seq is None:
        start_seq = random.choice(model.keys())
    rand_text = start_seq.lower()

    sentences = 0
    while sentences < sentence_count:
        rand_text += SEP + next_word(rand_text, N, counts)

        if rand_text.endswith((',', '.', '!', '?')):
            rand_text = rand_text + '\n\n'
            sentences += 1

    print(rand_text)
    return postprocess_output(rand_text)


def save_ngram_model(ngram_freqs, pkl_file):
    with open(pkl_file, 'wb') as output:
        pickle.dump(ngram_freqs, output, pickle.HIGHEST_PROTOCOL)


def load_ngram_model(pkl_file):
    with open(pkl_file, 'rb') as input:
        ngram_model = pickle.load(input)
    return ngram_model


def train_ngram_model(corpus_file, pkl_file, N=3):
    corpus = preprocess_corpus(corpus_file)

    ngrams = make_ngrams(corpus.split(SEP), N)
    ngram_model = ngram_freqs(ngrams)
    save_ngram_model(ngram_model, pkl_file)

    return ngram_model


def load_sample_input():
    data_path = 'static/model/generate/data/'
    happy_sample = []
    motivate_sample = []
    sad_sample = []

    file_location = data_path + "happy.json"
    file_stream = codecs.open(file_location, 'r', 'utf-8')
    jdata = json.load(file_stream)

    for data in jdata['Happy']:
        happy_sample.append(data['data'])

    file_location = data_path + "motivate.json"
    file_stream = codecs.open(file_location, 'r', 'utf-8')
    jdata = json.load(file_stream)

    for data in jdata['Motivate']:
        motivate_sample.append(data['data'])

    file_location = data_path + "sad.json"
    file_stream = codecs.open(file_location, 'r', 'utf-8')
    jdata = json.load(file_stream)

    for data in jdata['Sad']:
        sad_sample.append(data['data'])

    return happy_sample, motivate_sample, sad_sample
