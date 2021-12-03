# AI Project - Meeting Summary Generator - FALL 2021



## Overview / Description
The Meeting Summary Generator is a group project with group members Madison Adams and Ryan Laurents for the Fall 2021 semester of CSE 4308/5360-002 Artificial Intelligence. The Meeting Summary Generator is a web application that utilizes Machine Learning and Artificial Intelligence techniques. Initially, audio is converted into text using the textrank text summarization algorithm, and then converted text is summarized. The user has the choice to uploaded already recorded audio, record audio and then have that uploaded, or to upload text and have it summarized for them. Regardless of which option the user chooses, they receive summarized text in the end. The Meeting Summary Generator is programmed with Python and HTML/CSS and built and deployed through Flask, the python web framework.


## Tools Used / Dependencies
* Python3 version 3.6+
* Built-in python modules/packages:
    * os
    * shutil
    * glob
* Installed python modules/packages:
    * click==8.0.3
    * Flask==2.0.2
    * itsdangerous==2.0.1
    * Jinja2==3.0.3
    * joblib==1.1.0
    * MarkupSafe==2.0.1
    * networkx==2.6.3
    * nltk==3.6.5
    * numpy==1.21.4
    * pydub==0.25.1
    * regex==2021.11.10
    * scipy==1.7.3
    * SpeechRecognition==3.8.1
    * tqdm==4.62.3
    * Werkzeug==2.0.2


## How to Run
1. Unzip the AI_Project.zip file. This should create the AI_Project folder with its contents within it
2. Open a terminal/command prompt and navigate to the AI_Project directory
3. Create the virtual environment by running: python3 -m venv AI_Project
4. Activate the virtual environment.
    * On Windows, run: Scripts\activate.bat
    * On Linux/Unix or macOS, run: source bin/activate
5. Install the dependencies/modules by running: pip3 install -r requirements.txt
6. Start the web application by running: flask run
7. Navigate to http://localhost:5000/ or http://127.0.0.1:5000/ in your web browser.
8. The Meeting Summary Generator should now be successfully running! Use as needed.


## Sources
* https://towardsdatascience.com/understand-text-summarization-and-create-your-own-summarizer-in-python-b26a9f09fc70
* https://www.geeksforgeeks.org/python-text-summarizer/
* https://www.analyticsvidhya.com/blog/2019/06/comprehensive-guide-text-summarization-using-deep-learning-python/
* https://pythonrepo.com/repo/jiaaro-pydub-python-audio
* https://www.thepythoncode.com/article/using-speech-recognition-to-convert-speech-to-text-python
* https://towardsdatascience.com/easy-speech-to-text-with-python-3df0d973b426
* https://docs.python.org/3/tutorial/venv.html
* https://stackoverflow.com/



## License (MIT License)

Copyright (c) 2021 Ryan Laurents (laurentsR) and Madison Adams (madileigh)

Permission is hereby granted, free of charge, to any person obtaining a copy
of this software and associated documentation files (the "Software"), to deal
in the Software without restriction, including without limitation the rights
to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
copies of the Software, and to permit persons to whom the Software is
furnished to do so, subject to the following conditions:

The above copyright notice and this permission notice shall be included in all
copies or substantial portions of the Software.

THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
SOFTWARE.
