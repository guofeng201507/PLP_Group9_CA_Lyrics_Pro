import os
import glob
import pandas as pd
from flask import Flask, request
from twilio.twiml.messaging_response import MessagingResponse
# from twilio.twiml.voice_response import Play, VoiceResponse
from joblib import load
from random import randrange
import service.audio_process as ap
import service.intent_classification as ic
import service.ngram_text_generator as ntg

app = Flask(__name__)
app.config['SEND_FILE_MAX_AGE_DEFAULT'] = 0
intent_model = None
vectorizer = None
lyrics_gen_model = None
sentiment_intel = None
similarity_intel = None
context = ''
state = ''
last_resp_msg = ''

artist_final = ''
genre_final = ''


@app.route("/", methods=["POST"])
def main():
    base_url = request.base_url
    body = request.values.get('Body', None)
    media_url = request.values.get('MediaUrl0', None)
    covert_text = ''
    intent = ''
    resp_msg = ''
    continue_flag = True
    image_flag = False
    global context
    global state
    global last_resp_msg
    print("Current context: " + context)
    print("Current state: " + state)

    if media_url != '' and media_url is not None:
        print(media_url)
        file_name = ap.get_audio_content(media_url)
        des_filename = ap.convert_audio_format(file_name)
        covert_text = ap.covert_audio_to_text(des_filename)
    else:
        covert_text = body

    if covert_text is not None:
        print('Getting text body: ' + covert_text)

        pred_intent = ic.intent_classify(intent_model, vectorizer, covert_text)
        intent = str(pred_intent).replace("[", "").replace("]", "").replace("'", "")
        print('Getting intent: ' + str(intent))
        if intent == 'exit':
            continue_flag = False
        elif context != '':
            intent = 'ignored'
        print("After checking intent: " + intent)
    if continue_flag:
        if intent == 'ignored':
            if context == 'generate':
                sample_type = covert_text
                happy_sample, motivate_sample, sad_sample = ntg.load_sample_input()
                if "happy" in sample_type.lower():
                    index = randrange(10)
                    input_lyrics = happy_sample[index]
                elif "motivat" in sample_type.lower():
                    index = randrange(10)
                    input_lyrics = motivate_sample[index]
                elif "sad" in sample_type.lower():
                    index = randrange(10)
                    input_lyrics = sad_sample[index]
                else:
                    input_lyrics = sample_type

                print(input_lyrics)
                try:
                    resp_msg = "*Input lyrics:* _" + input_lyrics + "_\r\n"
                    resp_msg += "*Generated lyrics:* \r\n"
                    resp_msg += ntg.gengram_sentence(lyrics_gen_model, sentence_count=15, start_seq=input_lyrics)

                    context = ''
                    state = ''
                except KeyError:
                    resp_msg = "Sorry, that's not in my corpus. Please try other words. \r\n"
                    resp_msg += last_resp_msg
            elif context == 'find':
                song_name = covert_text
                indexs = similarity_intel.loc[similarity_intel['song_title'].str.lower() == song_name.lower()].index.values
                index_list = indexs.tolist()
                print("Size of result list: " + str(len(index_list)))
                if len(index_list) == 0:
                    resp_msg = "Sorry, I can't find this song in my database. Please try again. \r\n"
                    resp_msg += last_resp_msg
                else:
                    resp_msg = "*Song name:* _" + song_name + "_\r\n"
                    resp_msg += "*Number of songs matched:* " + str(len(index_list)) + "\r\n"
                    for i in index_list:
                        resp_msg += "*Artist name:* " + similarity_intel.loc[i, 'artist'] + "\r\n"
                        resp_msg += "*Sentiment:* " + sentiment_intel.loc[i, 'combined'] + "\r\n"
                        resp_msg += "*Similar songs:* " + similarity_intel.loc[i, 'bm25_songs'] + "\r\n"
                    context = ''
                    state = ''
            elif context == 'recom':
                if state == 'artist':
                    global artist_final
                    artist_name = covert_text
                    found_artist = True
                    if artist_name.lower() == 'skip':
                        artist_final = ''
                    else:
                        indexs = main_intel.loc[
                            main_intel['artist'].str.contains(artist_name, case=False)].index.values
                        index_list = indexs.tolist()
                        if len(index_list) == 0:
                            found_artist = False

                    if found_artist:
                        resp_msg = "Any preferred genre? Like Rock'n'Roll/Dance/Instrument/Rap \r\n" \
                                   "Doesn't have a particular? Use *Skip* to next step \r\n" \
                                   "Or you can use _*Exit*_ to restart again"
                        if artist_name.lower() != 'skip':
                            artist_final = artist_name
                        else:
                            artist_final = ''
                        state = 'genre'
                    else:
                        resp_msg = "No artist name: *" + artist_name + "* not found. Please try again. \r\n" \
                                   "Doesn't have a particular? Use *Skip* to next step \r\n" \
                                   "Or you can use _*Exit*_ to restart again"
                elif state == 'genre':
                    global genre_final
                    genre_type = covert_text
                    if genre_type.lower() == 'skip':
                        genre_final = 'wks_on_chart'
                    elif 'rock' in genre_type or 'roll' in genre_type:
                        genre_final = 'energy'
                    elif 'dance' in genre_type:
                        genre_final = 'danceability'
                    elif 'instrument' in genre_type:
                        genre_final = 'instrumentalness'
                    elif 'rap' in genre_type:
                        genre_final = 'speechiness'
                    else:
                        genre_final = 'wks_on_chart'

                    if artist_final != '':
                        filter_list = main_intel.loc[main_intel['artist'].str.contains(artist_final, case=False)]
                    else:
                        filter_list = main_intel.loc[main_intel['wks_on_top1'] > 0]
                    final_list = filter_list.sort_values(by=[genre_final], ascending=False)
                    artist_list = final_list['artist'].values.tolist()
                    title_list = final_list['song_title'].values.tolist()
                    tone_list = final_list['tone'].values.tolist()
                    url_list = final_list['url'].values.tolist()
                    list_size = 0
                    if len(title_list) > 5:
                        list_size = 5
                    else:
                        list_size = len(title_list)

                    resp_msg = "Recommend songs: \r\n"
                    for i in range(list_size):
                        resp_msg += "Song name: *" + title_list[i] + "* \r\n"
                        resp_msg += "Artist name: " + artist_list[i] + " \r\n"
                        resp_msg += "Tone: " + tone_list[i] + " \r\n"
                        resp_msg += "URL: " + url_list[i] + " \r\n"
                    context = ''
                    state = ''
                    artist_final = ''
                    genre_final = ''

        else:
            if intent == 'generate':
                context = 'generate'
                resp_msg = "which type of song you want to generate? (e.g. sad/happy/motivating or " \
                           "just start typing)\r\n" \
                           "Or you can use _*Exit*_ to restart again"
                last_resp_msg = resp_msg
                state = 'choose_type'
            elif intent == 'find':
                context = 'find'
                resp_msg = "What's the name of the song that you have? \r\n" \
                           "Or you can use _*Exit*_ to restart again"
                last_resp_msg = resp_msg
                state = 'input_song_name'
            elif intent == 'recom':
                context = 'recom'
                resp_msg = "What's the name of the artist on your mind? \r\n" \
                           "Doesn't have a particular? Use *Skip* to next step \r\n" \
                           "Or you can use _*Exit*_ to restart again"
                last_resp_msg = resp_msg
                state = 'artist'
            elif intent == 'greet':
                context = ''
                state = ''
                last_resp_msg = ''
                image_flag = True
                resp_msg = "Hello there! Welcome to use *Lyrics Pro*. You can: \r\n" \
                           "- Generate Lyrics\r\n" \
                           "- Find a similar song\r\n" \
                           "- Recommend a song"
    else:
        context = ''
        state = ''
        last_resp_msg = ''
        image_flag = True
        resp_msg = "Hello there! Welcome to use *Lyrics Pro*. You can: \r\n" \
                   "- Generate Lyrics\r\n" \
                   "- Find a similar song\r\n" \
                   "- Recommend a song"

    resp = MessagingResponse()
    # Add a message
    msg = resp.message(resp_msg)
    if image_flag:
        print(base_url)
        msg.media(base_url + "static/Lyrics_Pro.png")

    # resp = VoiceResponse()
    # resp.play('https://api.twilio.com/cowbell.mp3')
    # resp.play('https://32d832c5d1df.ngrok.io/static/book_a_room.wav')

    return str(resp)


if __name__ == '__main__':

    from argparse import ArgumentParser

    parser = ArgumentParser()
    parser.add_argument('-p', '--port', default=5001, type=int, help='port to listen on')
    args = parser.parse_args()
    port = args.port

    print("Clearing audio files")
    files = glob.glob('static/audio/*')
    for f in files:
        try:
            os.remove(f)
        except OSError as e:
            print("Error: %s : %s" % (f, e.strerror))

    print("Loading Intent Classification Model")
    intent_model = load('static/model/intent/clr_svm.joblib')

    print("Training Vectorizer")
    vectorizer = ic.train_model()

    print("Loading Lyrics Generation Model")
    lyrics_gen_model = ntg.load_ngram_model('static/model/generate/model_lyrics.pkl')

    print("Loading Song Intelligence")
    sentiment_intel = pd.read_csv('static/intel/sentiments.csv')
    similarity_intel = pd.read_csv('static/intel/text_similarity.csv')
    main_intel = pd.read_csv('static/intel/billboard100_final.csv')

    app.run(host='0.0.0.0', port=port, debug=True)
