import subprocess
import uuid
import requests
import speech_recognition as sr

audio_path = 'static/audio/'


def get_audio_content(media_url):
    file_name = audio_path + str(uuid.uuid4()) + '.oga'
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
