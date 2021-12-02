from flask import Flask, render_template, request, flash, redirect, send_file
import os
import shutil
from pydub import AudioSegment
from pydub.silence import split_on_silence
import speech_recognition as sr
from nltk.corpus import stopwords
from nltk.cluster.util import cosine_distance
import numpy as np
import networkx as nx
import glob

app = Flask(__name__)

app.secret_key = 'super super secret key'

# CHANGE THIS TO YOUR OWN BASE DIRECTORY
baseDirectory = 'D:/Ryans School/CSE 4308 - Artificial Intelligence/Project/AI_Website/'

def speechToText(audio):
    r = sr.Recognizer()
    with sr.AudioFile(audio) as source:
        audio_data = r.record(source)
        text = r.recognize_google(audio_data)
    return text

r = sr.Recognizer()
def get_large_audio_transcription(path, silenceLength):
    """
    Splitting the large audio file into chunks
    and apply speech recognition on each of these chunks
    """
    # open the audio file using pydub
    sound = AudioSegment.from_file(path)
    # split audio sound where silence is 700 miliseconds or more and get chunks
    chunks = split_on_silence(sound,
        # experiment with this value for your target audio file
        min_silence_len = silenceLength,
        # adjust this per requirement
        silence_thresh = sound.dBFS-14,
        # keep the silence for 1 second, adjustable as well
        keep_silence=500,
    )
    folder_name = "audio-chunks"
    # create a directory to store the audio chunks
    if not os.path.isdir(folder_name):
        os.mkdir(folder_name)
    else:
        shutil.rmtree(folder_name)
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
                whole_text += text
    # return the text for all chunks detected
    return whole_text

def sentence_similarity(sent1, sent2, stopwords=None):
    if stopwords is None:
        stopwords = []

    sent1 = [w.lower() for w in sent1]
    sent2 = [w.lower() for w in sent2]

    all_words = list(set(sent1 + sent2))

    vector1 = [0] * len(all_words)
    vector2 = [0] * len(all_words)

    # build the vector for the first sentence
    for w in sent1:
        if w in stopwords:
            continue
        vector1[all_words.index(w)] += 1

    # build the vector for the second sentence
    for w in sent2:
        if w in stopwords:
            continue
        vector2[all_words.index(w)] += 1

    return 1 - cosine_distance(vector1, vector2)

def read_article(file_name):
    file = open(file_name, "r")
    filedata = file.readlines()
    article = filedata[0].split(". ")
    sentences = []

    for sentence in article:
        print(sentence)
        sentences.append(sentence.replace("[^a-zA-Z]", " ").split(" "))
    sentences.pop()

    return sentences

def build_similarity_matrix(sentences, stop_words):
    # Create an empty similarity matrix
    similarity_matrix = np.zeros((len(sentences), len(sentences)))

    for idx1 in range(len(sentences)):
        for idx2 in range(len(sentences)):
            if idx1 == idx2: #ignore if both are same sentences
                continue
            similarity_matrix[idx1][idx2] = sentence_similarity(sentences[idx1], sentences[idx2], stop_words)

    return similarity_matrix

def generate_summary(text, top_n):
    stop_words = stopwords.words('english')
    summarize_text = []

    # Step 1 - Read text anc split it
    sentences =  read_article(text)
    numSentences = len(sentences)

    # Step 2 - Generate Similary Martix across sentences
    sentence_similarity_martix = build_similarity_matrix(sentences, stop_words)

    # Step 3 - Rank sentences in similarity martix
    sentence_similarity_graph = nx.from_numpy_array(sentence_similarity_martix)
    scores = nx.pagerank(sentence_similarity_graph)

    # Step 4 - Sort the rank and pick top sentences
    ranked_sentence = sorted(((scores[i],s) for i,s in enumerate(sentences)), reverse=True)

    requestedSentences = top_n
    if(numSentences < requestedSentences):
        requestedSentences = numSentences

    for i in range(requestedSentences):
        summarize_text.append(" ".join(ranked_sentence[i][1]))


    # Step 5 - Offcourse, output the summarize text
    f = open("summary.txt", "w")
    f.write(". ".join(summarize_text))
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
            fullText = get_large_audio_transcription(file, silenceLength)
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
            fullText = get_large_audio_transcription(file, silenceLength)
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
