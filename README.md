# Quran Voice Recognition

## Purpose
Sometimes you hear a beautiful Quran recitation or remember a couple words, but you don't know what surah and ayah it is. This project aims to support voice queries for identification of Quranic verses. 

## Projects that this one builds off of
- [Alfanous (for text matching)](https://github.com/assem-ch/alfanous)
- [Speech Recognition (for STT)](https://github.com/Uberi/speech_recognition)

## Installation
#### OSX
1. Make sure you have [Homebrew](http://brew.sh) installed and then run the following commands in terminal:
  1. `brew install portaudio`
  2. `brew install flac`
2. Clone this repo and navigate to it in terminal
3. Run the following commands in the parent directory of the project
  1. `virtualenv -p /usr/bin/python2.7 venv`
  2. `source venv/bin/activate`
  3. `pip install -r requirements.txt`

