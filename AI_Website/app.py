# Madison Adams and Ryan Laurents
# CSE 4308 - Artificial Intelligence
# Due 12/2/2021
# Term Project - Meeting Summary Generator

# Project Details:
# This repository runs a web app which allows a user to record or upload audio or text
# and the page will return a summary text file for the user to download. We also provide
# the full transcription of audio files available for download. There are some custom 
# variables that we allow the user to adjust: Silence Length and Number of Sentences in
# the summary. The Silence length variable is the minimum length of silence we wait before
# splitting them into separate sentences.

from flask import Flask, render_template, request, flash, redirect, send_file
import os
import shutil
from pydub import AudioSegment
from pydub.silence import split_on_silence
import speech_recognition as sr
import nltk
from nltk.corpus import stopwords
from nltk.cluster.util import cosine_distance
import numpy as np
import networkx as nx
import glob

nltk.download('stopwords')

app = Flask(__name__)

app.secret_key = 'super super secret key'

# CHANGE THIS TO YOUR OWN BASE DIRECTORY
baseDirectory = 'D:/Ryans School/CSE 4308 - Artificial Intelligence/Project/AI_Website/'

# This function splits a long audio file based on the user input silence length
# Each split is considered a different sentence later on
r = sr.Recognizer()
def transcribeLargeAudioFile(path, silenceLength):

    sound = AudioSegment.from_file(path)

    # split audio sound where silence is silenceLength milliseconds or more and get the chunks
    chunks = split_on_silence(sound,
        min_silence_len = silenceLength,
        # adjust this per requirement
        silence_thresh = sound.dBFS-14,
        keep_silence=500,
    )

    folderName = "audio-chunks"
    # create a directory to store the audio chunks
    if not os.path.isdir(folderName):
        os.mkdir(folderName)
    else:
        shutil.rmtree(folderName)
        os.mkdir(folderName)
    fullText = ""

    # Process chunks
    for i, audioChunk in enumerate(chunks, start=1):

        chunkFileName = os.path.join(folderName, f"chunk{i}.wav")
        audioChunk.export(chunkFileName, format="wav")

        with sr.AudioFile(chunkFileName) as source:
            audio = r.record(source)
            # try converting it to text
            try:
                text = r.recognize_google(audio)
            except sr.UnknownValueError as e:
                print("Error:", str(e))
            else:
                text = f"{text.capitalize()}. "
                fullText += text
    
    return fullText

# Calculate the cosine similarity between sentences
def cosineSimilarity(sent1, sent2, stopwords=None):
    if stopwords is None:
        stopwords = []

    sent1 = [w.lower() for w in sent1]
    sent2 = [w.lower() for w in sent2]

    allWords = list(set(sent1 + sent2))

    vector1 = [0] * len(allWords)
    vector2 = [0] * len(allWords)

    # Build the vector for the first sentence
    for w in sent1:
        if w in stopwords:
            continue
        vector1[allWords.index(w)] += 1

    # Build the vector for the second sentence
    for w in sent2:
        if w in stopwords:
            continue
        vector2[allWords.index(w)] += 1

    return 1 - cosine_distance(vector1, vector2)

# Grab the sentences from the text file.
def readText(file_name):
    file = open(file_name, "r")
    fileData = file.readlines()
    article = fileData[0].split(". ")
    sentences = []

    for sentence in article:
        print(sentence)
        sentences.append(sentence.replace("[^a-zA-Z]", " ").split(" "))
    sentences.pop()

    return sentences

# Build the similarity matrix so we can return the top n
def buildSimilarityMatrix(sentences, stopWords):
    # Create an empty similarity matrix
    similarityMatrix = np.zeros((len(sentences), len(sentences)))

    for i in range(len(sentences)):
        for j in range(len(sentences)):
            if i == j: #ignore if both are same sentences
                continue
            similarityMatrix[i][j] = cosineSimilarity(sentences[i], sentences[j], stopWords)

    return similarityMatrix


def generate_summary(text, top_n):
    stopWords = stopwords.words('english')
    summary = []

    # Read text and split the sentences
    sentences =  readText(text)
    numSentences = len(sentences)

    # Generate the cosine similarity for all sentences
    sentenceSimilarity = buildSimilarityMatrix(sentences, stopWords)

    # Rank sentences based on similarity score
    similarityGraph = nx.from_numpy_array(sentenceSimilarity)
    scores = nx.pagerank(similarityGraph)

    # Sort by rank and choose the top n sentences
    orderedSentences = sorted(((scores[i],s) for i,s in enumerate(sentences)), reverse=True)

    requestedSentences = top_n
    if(numSentences < requestedSentences):
        requestedSentences = numSentences

    for i in range(requestedSentences):
        summary.append(" ".join(orderedSentences[i][1]))


    # Write top n sentences to downloadable file
    f = open("summary.txt", "w")
    f.write(". ".join(summary))
    f.close()

@app.route("/")
def home():
    return render_template('dashboard.html')

@app.route('/upload/')
def upload():
    return render_template('upload.html')

@app.route('/upload/', methods=['POST'])
def uploadFile():
    if request.method == 'POST':
        try:
            file = request.files['file']
            silenceLength = int(request.form['silenceLength'])
            fullText = transcribeLargeAudioFile(file, silenceLength)
            textFile = open("fullText.txt", "w")
            textFile.write(fullText)
            textFile.close()
            n = int(request.form['n'])
            generate_summary("fullText.txt", n)
            fullText = "fullText.txt"
            summary = "summary.txt"
            return render_template('upload.html', fullText=fullText, summary=summary)
        except:
            flash(f"Unexpected error when uploading file, please try again.")
            return redirect('/upload/')

@app.route('/upload/<path:filename>', methods=['GET'])
def downloadFile(filename):
    # Root folder for project
    return send_file(filename, as_attachment=True)

@app.route('/record/')
def record():
    return render_template('record.html')

@app.route('/save-record/', methods=['GET', 'POST'])
def save_record():
    if 'file' not in request.files:
        flash('No file part')
        return redirect(request.url)
    file = request.files['file']
    if file.filename == '':
        flash('No selected file')
        return redirect(request.url)
    defaultName = "Recording"
    file_name = defaultName + ".mp3"
    # Root folder for the app + recordings
    full_file_name = os.path.join(baseDirectory, 'recordings', file_name)
    count = 0
    while(os.path.isfile(full_file_name)):
        count += 1
        if(count > 1):
            defaultName = defaultName[:9]
            defaultName += '['+str(count)+']'
        else:
            defaultName += '['+str(count)+']'
        file_name = defaultName + ".mp3"
        # Root folder + recordings 
        full_file_name = os.path.join(baseDirectory, 'recordings', file_name)
    file.save(full_file_name)
    return render_template('record.html')

@app.route('/summarize/', methods=['POST'])
def summarizeFile():
    if request.method == 'POST':
        try:
            # Get most recent recording
            folderPath = baseDirectory + 'recordings'
            fileType = '\*mp3'
            files = glob.glob(folderPath + fileType)
            maxFile = max(files, key = os.path.getctime)
            file = maxFile

            silenceLength = int(request.form['silenceLength'])
            fullText = transcribeLargeAudioFile(file, silenceLength)
            textFile = open("fullText.txt", "w")
            textFile.write(fullText)
            textFile.close()
            n = int(request.form['n'])
            generate_summary("fullText.txt", n)
            fullText = "fullText.txt"
            summary = "summary.txt"
            return render_template('record.html', fullText=fullText, summary=summary)
        except:
            flash(f"Unexpected error when uploading file, please try again.")
            return redirect('/record/')

@app.route('/record/<path:filename>', methods=['GET'])
def downloadSummary(filename):
    # Root folder for project
    return send_file(filename, as_attachment=True)

@app.route('/textUpload/')
def textUpload():
    return render_template('textUpload.html')

@app.route('/textUpload/', methods=['POST'])
def uploadTextFile():
    if request.method == 'POST':
        try:
            file = request.files['file']
            file.save('temp.txt')
            n = int(request.form['n'])
            generate_summary("temp.txt", n)
            summary = "summary.txt"
            return render_template('textUpload.html', summary=summary)
        except:
            flash(f"Unexpected error when uploading file, please try again.")
            return redirect('/textUpload/')

@app.route('/textUpload/<path:filename>', methods=['GET'])
def downloadTextFile(filename):
    # Root folder for project
    return send_file(filename, as_attachment=True)
    path = os.getcwd() + '/' + filename
    print(path)
    return send_file(path, as_attachment=True)

@app.route('/favicon.ico')
def favicon():
    return send_from_directory(os.path.join(app.root_path, 'static'),
                               'favicon.ico', mimetype='image/vnd.microsoft.icon')
