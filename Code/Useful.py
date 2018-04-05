"""
Scratchpad for useful functions and code
"""


# # Delay time example
# import time
# print("before")
# time.sleep(1.5)
# print("after")
#
#
# # Example console interactions
# print("Please type something:")
# string = input()
# print("You typed:", string)
#
#
# # Write to a file example
# fileObject = open("test.txt", 'w')
# fileObject.write("Testing 1 2 3, can you hear me?\nNope\nHa, ha, ha. Very funny\nWhat was that?")
# fileObject.close()
#
#
# # Read from a file example
# fileObject = open("test.txt", 'r')
# fileContents = fileObject.read()
# print(fileContents)
# fileObject.close()
#
#
# # Type conversion example
# print(str(int("7"*7)/7))  # Always works
# try:
#     var = int("bob")
# except ValueError:
#     print("Bob is not a number")
#
#
# # Printing to console in different colours:
# class Colours:
#     HEADER = '\033[95m'
#     OK_BLUE = '\033[94m'
#     OK_GREEN = '\033[92m'
#     WARNING = '\033[93m'
#     FAIL = '\033[91m'
#     END_TEXT = '\033[0m'
#     BOLD = '\033[1m'
#     UNDERLINE = '\033[4m'
#
#
# print(Colours.WARNING + "Insert Coloured Text Here!!!" + Colours.END_TEXT)
#
#
# # Valid file & folder detection
# # [^\/\\\:\*\?\"\<\>\|\W]+\)[^\/\\\:\*\?\"\<\>\|\W]*\.(txt|csv)
# import os, glob
# folders = glob.glob('*)*' + os.path.sep)
# files = glob.glob("*)*.*")
#
#
# # Regular Expression Example:
# import re
# string = "\t hello _ world\t!"
# regex = "[\s]+"
# result = re.sub(regex, "", string, flags=re.MULTILINE)
# removed = re.findall(regex, string, flags=re.MULTILINE)
# print(regex + "\n" + string + "\n" + result)
# print(removed)
#
#
# # Regular Expressions
# # https://regex101.com/
# # Comments inc prior whitespace:
# #   \s*\/\/[\S\t ]*
# # Insert into Map code:
# #   \n#[A-Z][a-zA-Z_]*,[ \t]*[^\s\\\:\*\?\"\<\>\|\n\r\0]*\n
# # Extract from Map code:
# #   \n#[A-Z][a-zA-Z_]*,?[ \t]*
# # Code block start & end detection (\n###\n)
# #   \n#{3}\n[\s\S]{0,}?\n#{3}\n?
# # White-space detection (for removal)
# #   [\s]+
#
#
# # Map / Dictionary Example:
# map_ = {"key": 'value', "num": 5318008, "bin": True}
# map_.update({"life": "death"})
# print(str(map_["key"]) + ", " + str(map_["num"]) + ", " + str(map_["bin"]) + ", " + str(map_["life"]))
#
#
# //////////////////////////////////////////////////////////////////////////////////////////////////////////////
# //////////////////////////////////////////////////////////////////////////////////////////////////////////////
# /// MULTIPROCESSING EXAMPLE
# //////////////////////////////////////////////////////////////////////////////////////////////////////////////
# //////////////////////////////////////////////////////////////////////////////////////////////////////////////
#
# import time
# import multiprocessing as mp
# import winsound
#
# def worker(x, i):
#     x[i] += [i]
#     winsound.PlaySound('wrong.wav', winsound.SND_FILENAME)
#
#
#
# def func(val, lock):
#     for i in range(50):
#         time.sleep(0.01)
#         with lock:
#             val.value += 1
#
#
# def main():
#     v = mp.Value('i', 0)
#     lock = mp.Lock()
#     process = [mp.Process(target=func, args=(v,lock)) for i in range(10)]
#     for p in process:
#         p.start()
#     for p in process:
#         p.join()
#     print(v.value)
#
#     num = 20
#     x = mp.Manager().list([[]]*num)
#     print(x)
#     p = []
#     for i in range(num):
#         p.append(mp.Process(target=worker, args=(x, i)))
#         p[i].start()
#
#     for i in range(num):
#         p[i].join()
#
#     print(x)
#
#
# if __name__ == '__main__':
#     main()
#
# ///////////////////////////////////////////////////////////////////////
# /// TEXT TO SPEECH EXAMPLES:
# ///////////////////////////////////////////////////////////////////////
# # Offline using the os-specific text to speech converter
# import win32com.client
# speaker = win32com.client.Dispatch("SAPI.SpVoice")
# speaker.Speak("Jump-man Jump-man Jump-man Them boys up to something!")
#
#
# # Online with Google API:
# from gtts import gTTS
# import winsound
# text = "Jump-man Jump-man Jump-man. Them boys up to something!"
# tts = gTTS(text=text, lang='en')
# tts.save('speech.mp3')
# # Convert to wav file... or find another alternative
# winsound.PlaySound('speech.wav', winsound.SND_FILENAME)
#
#
#
#
# ////////////////////////////////////////////////////////////////////////////
# /// SPEECH TO TEXT CONVERSION EXAMPLE!
# ////////////////////////////////////////////////////////////////////////////
#
# Standard beginnings:
from pprint import pprint
import speech_recognition as sr
r = sr.Recognizer()
with sr.Microphone() as source:
    print("Say something!")
    audio = r.listen(source)

# Offline translation using CMUSphinx:
try:
    print("You said: " + r.recognize_sphinx(audio))
    print(str(r.recognize_sphinx(audio, show_all=True)))
except sr.UnknownValueError:
    print("Sphinx could not understand audio")
    pass
except sr.RequestError as e:
    print("Sphinx error; {0}".format(e))
    pass

# Online translation using Google's API:
try:
    # for testing purposes, we're just using the default API key
    # to use another API key, use `r.recognize_google(audio, key="GOOGLE_SPEECH_RECOGNITION_API_KEY")`
    # instead of `r.recognize_google(audio)`
    print(r.recognize_google(audio, show_all=False))
    pprint(r.recognize_google(audio, show_all=True))
except sr.UnknownValueError:
    print("Google Speech Recognition could not understand audio")
    pass
except sr.RequestError as e:
    print("Could not request results from Google Speech Recognition service; {0}".format(e))
    pass
