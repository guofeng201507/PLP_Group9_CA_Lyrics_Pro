from flask import Flask, request
import requests
import subprocess
import uuid
from twilio.twiml.messaging_response import MessagingResponse
# from twilio.twiml.voice_response import Play, VoiceResponse
import speech_recognition as sr

app = Flask(__name__)
app.config['SEND_FILE_MAX_AGE_DEFAULT'] = 0


def get_audio_content(media_url):
    file_name = str(uuid.uuid4()) + '.oga'
    response = requests.get(media_url)
    byte_content = response.content
    print("Byte content: " + str(byte_content))
    with open(file_name, 'wb') as out:
        out.write(byte_content)
    print("Saved to file: " + file_name)
    return file_name


def convert_audio_format(file_name):
    src_filename = file_name
    dest_filename = file_name.split('.')[0] + '.wav'

    process = subprocess.run(['ffmpeg', '-i', src_filename, dest_filename])
    print("Convert audio format to: " + dest_filename)
    return dest_filename


def covert_audio_to_text(file_name):
    covert_text = ''
    r = sr.Recognizer()

    with sr.AudioFile(file_name) as source:
        r.adjust_for_ambient_noise(source)

        print("Converting Audio To Text ..... ")

        audio = r.listen(source)

    try:
        covert_text = r.recognize_google(audio)
        print("Converted Audio Is : \n" + covert_text)

    except Exception as e:
        print("Error {} : ".format(e))

    return covert_text


@app.route("/", methods=["POST"])
def main():
    body = request.values.get('Body', None)
    media_url = request.values.get('MediaUrl0', None)
    covert_text = ''

    if media_url != '' and media_url is not None:
        print(media_url)
        file_name = get_audio_content(media_url)
        des_filename = convert_audio_format(file_name)
        covert_text = covert_audio_to_text(des_filename)
    else:
        covert_text = body
        print(body)

    resp = MessagingResponse()
    if covert_text == '':
        covert_text = "Error understanding the audio"

    # Add a message
    msg = resp.message(covert_text)
    # msg.media("https://farm8.staticflickr.com/7090/6941316406_80b4d6d50e_z_d.jpg")

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

    app.run(host='0.0.0.0', port=port, debug=True)
