import speech_recognition as sr 
from gtts import gTTS
from playsound import playsound
import os

def cria_audio(audio, mensagem):
	tts = gTTS(mensagem, lang = 'pt-br', slow=False)
	tts.save(audio)
	print(mensagem)
	playsound(audio)
	os.remove(audio)

cria_audio("welcome.mp3", "Olá, sou a Ana! Vou reconhecer a sua voz. Diga algo")	

recon = sr.Recognizer()
#cria_audio("diga_algo.mp3","Diga algo")
with sr.Microphone() as source:

	
	try:
		audio = recon.listen(source, timeout = None)
		frase = (recon.recognize_google(audio, language = 'pt-br'))
		cria_audio("mensagem.mp3", frase)
	except sr.UnknownValueError:		
		# audio = recon.listen('erro', timeout = None)
		frase = "Desculpa, não consegui entender!"
		cria_audio("mensagem.mp3", frase)
	except sr.RequestError as e:
		frase = "Desculpa, não consegui entender!"
		cria_audio("mensagem.mp3", frase)




