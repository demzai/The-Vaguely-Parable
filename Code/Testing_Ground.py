"""
# This is the testing ground.
# Develop functions here, but do not leave them here!
# This is a glorified playground to make a mess in!
"""

# Dependencies:
import speech_recognition as sr

r = sr.Recognizer()

print('Please say "do not go anywhere":')
with sr.Microphone() as source:
    audio_en = r.listen(source)
print('Processing...')

try:
    print(r.recognize_google(audio_en))
    print(r.recognize_sphinx(audio_en))
    # noinspection SpellCheckingInspection
    print(r.recognize_sphinx(audio_en, grammar='Grammars/donotgoanywhere.gram'))
except sr.UnknownValueError:
    print("Sphinx could not understand audio")
except sr.RequestError as e:
    print("Sphinx error; {0}".format(e))

