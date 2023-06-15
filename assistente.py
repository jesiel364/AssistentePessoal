import os
import sys
import speech_recognition as sr 
import webbrowser as browser
import urllib.request, json, requests
import translate
from gtts import gTTS
from playsound import playsound
from datetime import datetime
from bs4 import BeautifulSoup
from requests import get
from translate import Translator

def cria_audio(audio, idioma,  mensagem):

	tts = gTTS(mensagem, lang = idioma, slow=False)
	tts.save(audio)
	print(mensagem)
	playsound(audio)
	os.remove(audio)

def digitar():
	res = input("Digite algo: ")
	executa_comandos(res)

def monitora_audio():
	recon = sr.Recognizer()
	recon.dynamic_energy_threshold = False
	with sr.Microphone() as source:
		while True:
			# print('Diga algo, estou te ouvindo')
			audio = recon.listen(source, phrase_time_limit=5)
			try: 
				mensagem = recon.recognize_google(audio, language = 'pt-br')
				mensagem = mensagem.lower()
				print('Você disse', mensagem)
				cria_audio("mensagem.mp3", "pt-br", f'{mensagem}?')
				executa_comandos(mensagem)
				break
			except sr.UnknownValueError:
				frase = "Desculpa, não consegui entender!"
				print(frase)
				# cria_audio("mensagem.mp3", frase)
				pass
			except sr.RequestError:
				frase = "Desculpa, não consegui entender!"
				cria_audio("mensagem.mp3", "pt-br", frase)
		return mensagem

def noticias():
	site = get('https://news.google.com/news/rss?ned=pt_br&gl=BR&hl=pt')
	noticias = BeautifulSoup(site.text, 'html.parser')
	for item in noticias.findAll('item')[:5]:
		mensagem = item.title.text
		print(mensagem)
		cria_audio("noticia.mp3", "pt-br", mensagem)



def cotacao(moeda):
	requisicao = get(f'https://economia.awesomeapi.com.br/all/{moeda}-BRL')
	cotacao = requisicao.json()
	nome = cotacao[moeda]['name']
	data = cotacao[moeda]['create_date']
	valor = cotacao[moeda]['bid']
	cria_audio("cotacao.mp3", "pt-br", f"Cotação do {nome} em {data} é {valor}")

def filmes():
	token = "<suachaveapi>"
	url = 'https://api.themoviedb.org/3/discover/movie?sort_by=popularity.desc&api_key={token}'
	resposta = urllib.request.urlopen(url)
	dados = resposta.read()
	jsondata = json.loads(dados)
	filmes = jsondata = json.loads(dados)['results']
	for filme in filmes[:5]:
		cria_audio("filmes.mp3", "pt-br", filme['title'])

def clima(cidade):
	token = "<suachaveapi>"
	base_url = "http://api.openweathermap.org/data/2.5/weather?"
	complete_url = base_url + "appid=" + token + "&q=" + cidade
	response = requests.get(complete_url)
	retorno = response.json()
	if retorno["cod"] == 200:
	    valor = retorno["main"]
	    current_temperature = valor["temp"]
	    current_humidiy = valor["humidity"]
	    tempo = retorno["weather"]
	    weather_description = tempo[0]["description"]
	    clima = (f"Em {cidade} a temperatura é de {str(int(current_temperature - 273.15))} graus celcius e humidade de {str(current_humidiy)} %")
	    cria_audio("clima.mp3", "pt-br", clima)
	else:
		cria_audio("erro.mp3", "pt-br", "Infelizmente não entendi, pode repetir por favor?")

def tradutor(traducao):
	if traducao == 'inglês':
		traduz = Translator(from_lang="pt-br", to_lang='english')
		cria_audio("traducao.mp3", "pt-br", "O que você gostaria de traduzir para o inglês?")
		mensagem = monitora_audio()
		traduzido = traduz.translate(mensagem)
		cria_audio("traducao.mp3", f"A tradução de {mensagem} é")
		cria_audio("traducao_eng.mp3","en", traduzido)
	elif traducao == 'português':
		traduz = Translator(from_lang="english", to_lang='pt-br')
		cria_audio("traducao.mp3", "O que você gostaria de traduzir para o português?")
		mensagem = monitora_audio()
		traduzido = traduz.translate(mensagem)
		cria_audio("traducao.mp3", "pt-br", f"A tradução de")
		cria_audio("traducao_eng.mp3", "en", mensagem)
		cria_audio('traducao_port.mp3', "pt-br", f"é {traduzido}" )

def getResultadosGoogle(pesquisa):
	res = []
	site = get(f'https://google.com/search?q={pesquisa}')
	pagina = BeautifulSoup(site.text, 'html.parser')
	for item in pagina.find_all( 'span' ):
		res.append(item)

	# cria_audio("resultados.mp3", "pt-br", res[0])
	for i in res:
		print(i.getText())

def dicionario(pesquisa):
	res = []
	site = get(f'https://pt.wiktionary.org/wiki/{pesquisa}')
	pagina = BeautifulSoup(site.text, 'html.parser')
	for item in pagina.find_all( 'ol' ):
		res.append(item.getText())

	if res:
		cria_audio("significado.mp3", "pt-br", res[0])
	else:
		cria_audio('alerta.mp3', "pt-br", f'Nenhum resultado para {pesquisa}')

def wikipedia(pesquisa):
	res = []
	site = get(f'https://pt.wikipedia.org/wiki/{pesquisa}')
	pagina = BeautifulSoup(site.text, 'html.parser')
	for item in pagina.find_all( 'p' ):
		res.append(item.getText())

	if res:
		cria_audio("significado.mp3", "pt-br", f"{res[0]}")
	else:
		cria_audio('alerta.mp3', "pt-br", f'Nenhum resultado para {pesquisa}')

lista_de_comandos = ["Que horas são?", "Pesquisar objeto no Google", "Qual a cotação do dólar no momento?", "Quais as últimas notícias?",  "Quais os filmes mais populares no momento?", "Qual a melhor música do mundo?",  "Clima em São Paulo", "Traduzir para o inglês",  "Criar novo lembrete ou Visualizar lembretes", "Abrir Programa", "Desligar computador em uma hora", "Cancelar desligamento", "Fechar assistente"]

def executa_comandos(mensagem):

	# fechar assistente
	if 'fechar assistente' in mensagem or 'fechar' in mensagem or 'sair' in mensagem:
		cria_audio("alerta.mp3", "pt-br", "Fechando assistente")
		sys.exit()

	# hora atual
	elif 'horas' in mensagem:
		hora = datetime.now().strftime('%H:%M')
		frase = f"Agora são {hora}"
		cria_audio("horas.mp3", "pt-br", frase)

	# desligar o computador
	elif 'desligar computador' in mensagem and 'uma hora' in mensagem:
		cria_audio("horas.mp3", "pt-br", "o computador irá desligar em uma hora")
		os.system("shutdown -s -t 3600")
	elif 'desligar computador' in mensagem and 'meia hora' in mensagem:
		cria_audio("horas.mp3", "pt-br", "o computador irá desligar em meia hora")
		os.system("shutdown -s -t 1800")
	elif 'cancelar desligamento' in mensagem:
		cria_audio("horas.mp3", "pt-br", "Desligamento automático do computador cancelado")
		os.system("shutdown -a")

	# pesquisa no google
	elif 'pesquisa' in mensagem and 'google' in mensagem or 'como' in mensagem:
		print(mensagem)
		mensagem = mensagem.replace('pesquisar', '')
		mensagem = mensagem.replace('pesquisa', '')
		mensagem = mensagem.replace('google', '')
		mensagem = mensagem.replace('no', '')
		cria_audio("mensagem.mp3", "pt-br", f'Pesquisando {mensagem}')
		browser.open(f'https://google.com/search?q={mensagem}')
		



	# pesquisa no youtube
	elif 'pesquisa' in mensagem and 'youtube' in mensagem:
		mensagem = mensagem.replace('pesquisar', '')
		mensagem = mensagem.replace('pesquisa', '')
		mensagem = mensagem.replace('youtube', '')
		mensagem = mensagem.replace('no', '')
		cria_audio("mensagem.mp3", "pt-br", f'Pesquisando no youtube {mensagem}')
		browser.open(f'https://youtube.com/results?search_query={mensagem}')

	# spotify
	elif 'melhor' in mensagem and 'música' in mensagem:
		cria_audio("mensagem.mp3", "pt-br", f'Abrindo melhor música no Spotify')
		browser.open('https://open.spotify.com/track/2jvuMDqBK04WvCYYz5qjvG?si=d5118879d68540f3')
	elif 'melhor' in mensagem and 'banda' in mensagem:
		cria_audio("mensagem.mp3", "pt-br", f'Abrindo melhor banda no Spotify')
		browser.open('https://open.spotify.com/playlist/37i9dQZF1DZ06evO07zaak?si=2cc1a14c1146467a')
	elif 'melhor' in mensagem and 'álbum' in mensagem:
		cria_audio("mensagem.mp3", "pt-br", f'Abrindo melhor álbum no Spotify')
		browser.open('https://open.spotify.com/album/4LH4d3cOWNNsVw41Gqt2kv?si=9f6e7d7bcb474666')
	elif 'playlist' in mensagem and 'rock' in mensagem:
		cria_audio("mensagem.mp3", "pt-br", f'Abrindo playlist de Rock no Spotify')
		browser.open('https://open.spotify.com/playlist/5TUxgTIxzLbLVh7RUf9V8i?si=4567c0415d0647b1')
	elif 'playlist' in mensagem and 'eletronica' in mensagem:
		cria_audio("mensagem.mp3", "pt-br", f'Abrindo playlist de música eletrônica no Spotify')
		browser.open('https://open.spotify.com/playlist/2HszJWnlslyuye9GFZQJQc?si=81537070a51d4c97')
	elif 'playlist' in mensagem and 'brasileira' in mensagem:
		cria_audio("mensagem.mp3", "pt-br", f'Abrindo playlist de MPB no Spotify')
		browser.open('https://open.spotify.com/playlist/7ngeDvP8gp3ZtCGfq68jUV?si=49e62791666242a8')

	# notícias
	elif 'notícias' in mensagem:
		cria_audio("noticias.mp3", "pt-br", "Estas são as 5 principais nóticias de hoje")
		noticias()

	# cotação de moedas
	elif 'dólar' in mensagem:
		cotacao('USD')
	elif 'euro' in mensagem:
		cotacao('EUR')
	elif 'bitcoin' in mensagem:
		cotacao('BTC')

	# filmes
	elif 'filmes' in mensagem and 'populares' in mensagem:
		filmes()

	# clima
	elif 'clima' in mensagem:
		mensagem = mensagem.replace('clima', '')
		mensagem = mensagem.replace('em', '')
		clima(mensagem[2:])
	elif 'temperatura' in mensagem:
		mensagem = mensagem.replace('temperatura', '')
		mensagem = mensagem.replace('em', '')
		clima(mensagem[2:])

	# abrir programas do computador
	elif 'abrir' in mensagem and 'google chrome' in mensagem or 'abrir chrome' in mensagem:
		cria_audio("mensagem.mp3", "pt-br", f'Abrindo Chrome')
		os.startfile("C:/Program Files/Google/Chrome/Application/chrome.exe")
	elif 'abrir' in mensagem and 'Reaper' in mensagem:
		cria_audio('mensagem.mp3', "pt-br", "Abrindo Reaper")
		os.startfile("C:/Program Files/REAPER (x64)/reaper.exe")
	elif 'abrir' in mensagem and 'sublime text' in mensagem or 'abrir sublime' in mensagem:
		cria_audio("mensagem.mp3", "pt-br", f'Abrindo Sublime Text')
		os.startfile("C:/Program Files/Sublime Text/sublime_text.exe")
	elif 'abrir' in mensagem and 'cmd' in mensagem or 'prompt de comando' in mensagem:
		cria_audio("mensagem.mp3", "pt-br", f'Abrindo Prompt de comando')
		os.system("cmd")
	elif 'abrir' in mensagem and 'notion' in mensagem:
		os.startfile("<caminho para notion na sua máquina>")

	# tradutor
	elif 'traduzir' in mensagem and 'inglês' in mensagem:
		tradutor('inglês')
	elif 'traduzir' in mensagem and 'português' in mensagem:
		tradutor('português')

	# lembrete
	elif 'novo' in mensagem and 'lembrete' in mensagem:
		cria_audio("lembrete.mp3", "O que você gostaria de anotar no lembrete?")
		lembrete = monitora_audio()
		os.system(f'c: && cd C:/Program Files/Conceptworld/Notezilla && Notezilla.exe /CreateNewNote "{lembrete}"')
	elif 'mostrar' in mensagem and 'lembrete' in mensagem:
		os.system('c: && cd C:/Program Files/Conceptworld/Notezilla && Notezilla.exe /BringNotesOnTop')


	#listar comandos
	elif 'comandos' in mensagem or "mostrar comandos" in mensagem:
		cria_audio("mensagem.mp3", 'Estes são os comandos que poderá utilizar: ')
		for item in lista_de_comandos:
			cria_audio('comando.mp3', item)

	#dicionario
	elif 'significa' in mensagem or 'o que é' in mensagem:
		mensagem = mensagem.replace('significa', '')
		mensagem = mensagem.replace('wikipedia', '')
		mensagem = mensagem.replace('o que é', '')
		dicionario(mensagem)

	#wikipedia
	elif 'wikipedia' in mensagem or 'pesquisar na wikipedia' in mensagem:
		mensagem = mensagem.replace('wikipedia', '')
		mensagem = mensagem.replace('pesquisar na', '')
		wikipedia(mensagem)


def main():
	cria_audio("ola.mp3", "pt-br", "O que cê manda?")
	for item in lista_de_comandos:
		print(item)
	# cria_audio("ola.mp3", "Olá sou a Ana, sua assistente virtual! Como posso ajudar?")
	while True:
		# monitora_audio()
		digitar()


main()
