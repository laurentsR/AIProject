# Madison Adams and Ryan Laurents
# UTA CSE 4308 - Artificial Intelligence
# Term Project - Meeting Summarizer

import os
from pydub.silence import split_on_silence
from pydub import AudioSegment
# import pyaudio # possibly add in if we have time
import speech_recognition as speech
# Possibly import more or less from nltk (TBD)
from nltk.corpus import stopwords
from nltk.tokenize import word_tokenize, sent_tokenize

r = sr.Recognizer()

def uploadAudio(choice):
    if(choice):
        audioPath = input("Enter the file path for the audio file:")
        try:
            with open(audioPath):
                print(audioPath)
                audio = None
        except Exception as e:
            raise "An error has occurred: " + e
    return audio

def get_large_audio_transcription(path):
    """
    Splitting the large audio file into chunks
    and apply speech recognition on each of these chunks
    We need to split it based on pauses to add punctuation
    and capitalization
    """
    # open the audio file using pydub
    sound = AudioSegment.from_wav(path)
    # split audio sound where silence is 700 miliseconds or more and get chunks
    chunks = split_on_silence(sound,
        # experiment with this value for your target audio file
        min_silence_len = 500,
        # adjust this per requirement
        silence_thresh = sound.dBFS-14,
        # keep the silence for 1 second, adjustable as well
        keep_silence=500,
    )
    folder_name = "audio-chunks"
    # create a directory to store the audio chunks
    if not os.path.isdir(folder_name):
        os.mkdir(folder_name)
    whole_text = ""
    # process each chunk
    for i, audio_chunk in enumerate(chunks, start=1):
        # export audio chunk and save it in
        # the `folder_name` directory.
        chunk_filename = os.path.join(folder_name, f"chunk{i}.wav")
        audio_chunk.export(chunk_filename, format="wav")
        # recognize the chunk
        with sr.AudioFile(chunk_filename) as source:
            audio_listened = r.record(source)
            # try converting it to text
            try:
                text = r.recognize_google(audio_listened)
            except sr.UnknownValueError as e:
                print("Error:", str(e))
            else:
                text = f"{text.capitalize()}. "
                print(chunk_filename, ":", text)
                whole_text += text
    # return the text for all chunks detected
    return whole_text

def textSummarizer(generatedText):
    pass

def main():
    # For testing (remove later and get input from user in app):
    # choice = input("Enter 0 for recording or 1 for uploading an already recorded file:")

    # UNCOMMENT TO TEST THE TRANSCRIPTION CODE
    path = "test_conversion.wav"
    text = get_large_audio_transcription(path)
    print(text)

    # audio = uploadAudio(choice)
    # generatedText = speechToText(audio)
    # textSummarizer(generatedText)

if __name__ == '__main__':
    main()
