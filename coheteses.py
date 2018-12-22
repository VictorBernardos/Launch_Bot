from urllib.request import urlopen
import datetime
import json
import telegram
import time
from telegram.ext import Updater, CommandHandler, MessageHandler, BaseFilter

cohete_emoji = u'\U0001F680'
reloj_emoji = u'\U0001F550'
no_emoji = u'\U0000274C'
si_emoji = u'\U00002705'
warning_emoji = u'\U000126A0'

url = 'https://launchlibrary.net/1.4/launch'
TOKEN = "TOKEN"


print ('Bot iniciado') 
lista=[]

def añadir(bot,update):
	global lista
	if(update.message.chat_id in lista):#Comprobamos que esta en la lista
		bot.sendMessage(update.message.chat_id,"Ya estabas dentro de la lista")
		
		
	else:#Si no esta lo añadimos
		bot.sendMessage(update.message.chat_id, si_emoji +"Has sido correctamente agregado y a partir de ahora recibiras notificaciones"+ si_emoji)
		lista.append(update.message.chat_id)


def eliminar(bot,update):
	global lista
	if(update.message.chat_id in lista):
		lista.remove(update.message.chat_id)
		bot.sendMessage(update.message.chat_id,no_emoji+"Has sido correctamente eliminado de la lista y no recibiras notificaciones"+no_emoji)
	else:
		 bot.sendMessage(update.message.chat_id,"Para ser eliminado de la lista, primero debes estar en ella")
	
def estado (bot,update):

	global lista
	if(update.message.chat_id in lista):
		bot.sendMessage(update.message.chat_id, si_emoji)
	else:
		bot.sendMessage(update.message.chat_id, no_emoji)


def Hora(bot,update):
	bot.send_message(update.message.chat_id, "La hora es: " + time.strftime("%H:%M:%S"))
	print("La hora es"+ time.strftime("%H:%M:%S")) #voy a probar si imprimealgo cuando recibe el /hora

#Comprueba si hoy hay algun lanzamiento o no
def hay_lanzamiento():
	paquete = urlopen(url)
	datos = json.load(paquete)  
	array = datos['launches']
	dia_lanza = convertirhorario(array[0]).split(" ") [0]
	dia_actual = time.strftime("%d")
	#dia_actual = 'xx' #Degub forzar el deia para pruebas

	#print ('Hoy es ' + time.strftime("%d"))     #Debug
	#print ('Proximo lanzamiento ' + dia_lanza)  #Debug

	if (dia_actual == dia_lanza):
		print ('Hoy hay lanzamiento')           #Debug
		return (True)
	else:
		print ('Hoy NO hay lanzamiento')        #Debug
		return (False)

def convertirhorario(launchId):
	tiempo = launchId['net'].split(" ")
	horas = tiempo[3].split(":")
	h = int(horas[0])
	

	
	mes = ''

	if (tiempo[0] == 'January'):
		mes = 'Enero'
	elif (tiempo[0] == 'February'):
		mes = 'Febrero'
	elif (tiempo[0] == 'March'):
		mes = 'Marzo'
	elif (tiempo[0] == 'April'):
		mes = 'Abril'
	elif (tiempo[0] == 'May'):
		mes = 'Mayo'
	elif (tiempo[0] == 'June'):
		mes = 'Junio'
	elif (tiempo[0] == 'July'):
		mes = 'Julio'
	elif (tiempo[0] == 'August'):
		mes = 'Agosto'
	elif (tiempo[0] == 'September'):
		mes = 'Septiembre'
	elif (tiempo[0] == 'October'):
		mes = 'Octubre'
	elif (tiempo[0] == 'November'):
		mes = 'Noviembre'
	elif (tiempo[0] == 'December'):
		mes = 'Diciembre'
	else:
		mes = 'ERROR'

	coma = tiempo[1].split(",")
	dia = coma[0]
	
	if(h==23):
		h=1#Si son las 11 de la noche,convertimos la hora a la 1 de la mañana
		dia=int(dia)#Logicamente el dia aumenta para ello lo convertimos a entero
		dia=dia+1
	else:
		h=h+1

	
	return(str(dia) + " de " + mes + " " + tiempo[2] + " " + str(h) + ":" + horas[1] + ":" + horas[2] + ' (Hora Española)')

#Poniendo /lista nos saca la lista de lanzamientos
def launch(bot, update):
	paquete = urlopen(url)
	datos = json.load(paquete)   
	array = datos['launches']
	data = ''
	for i in range(0,len(array)):
		#print(array[(len(array)-i-1)] ['name'])  #Debug
		data = str(cohete_emoji + '<b>' + array [len(array) - i - 1] ['name'] + '</b>\n' + reloj_emoji + '<i>' + convertirhorario(array [len(array) - i - 1]) + '</i>\n') + data
	bot.sendMessage(update.message.chat_id, data,'HTML')

#Poniendo /next nos dice el siguiente lanzamiento y el enlace para poder verlo
def siguiente(bot,update):
	paquete = urlopen(url)
	datos = json.load(paquete)  
	array = datos['launches']
	data = ''
	#print(array[0] ['name'])       #Debug
	data = 'Próximo lanzamiento: \n' + str(cohete_emoji + '<b>' + array [0] ['name'] + '</b>\n' + reloj_emoji + '<i>' + convertirhorario(array[0]) + '</i>\n')
	bot.sendMessage(update.message.chat_id, data,'HTML')
	video = array [0] ['vidURLs']   # Eliminar  ["  "]
	print('a' + video + 'b')
	vid=video[0].split("[")
	bot.sendMessage(update.message.chat_id, vid[0])

def automatico(bot,chatid):
	paquete = urlopen(url)
	datos = json.load(paquete)  
	array = datos['launches']
	data = ''
	#print(array[0] ['name'])       #Debug
	
	data = 'Próximo lanzamiento: \n' + str(cohete_emoji + '<b>' + array [0] ['name'] + '</b>\n' + reloj_emoji + '<i>' + convertirhorario(array[0]) + '</i>\n')
	bot.sendMessage(chatid, data,'HTML')

	try:
		video = array [0] ['vidURLs']   

	except KeyError:
		print("No hay enlace de video")    

	else: 
		vid=video[0].split("[")
		bot.sendMessage(chatid, vid[0])


#Aviso automatico del siguiente lanzamiento a una hora programada
def callback_auto(bot, job):
	global lista
	for x in range(0,len(lista)):
		
		if(hay_lanzamiento()):
			automatico(bot,lista[x])
		else:
			bot.sendMessage(lista[x], 'Hoy no hay lanzamientos')


def start (bot, update):
	bot.send_message(update.message.chat_id, 'Este BOT te avisa de los ultimos lanzamientos de cohetes')


updater = Updater(TOKEN, workers=200)
dispatcher = updater.dispatcher

hora_handler = CommandHandler('hora', Hora)
dispatcher.add_handler(hora_handler)

launch_handler = CommandHandler('lista', launch)
dispatcher.add_handler(launch_handler)

next_handler = CommandHandler('next', siguiente)
dispatcher.add_handler(next_handler)

start_handler = CommandHandler('start', start)
dispatcher.add_handler(start_handler)

#debug_handler = CommandHandler('debug', debug)  #Debug
#dispatcher.add_handler(debug_handler)

añadir_handler = CommandHandler('añadir', añadir)  
dispatcher.add_handler(añadir_handler)

eliminar_handler = CommandHandler('eliminar', eliminar)  
dispatcher.add_handler(eliminar_handler)

estado_handler = CommandHandler('estado', estado)
dispatcher.add_handler(estado_handler)

job = updater.job_queue
job.run_daily(callback_auto, time=datetime.time(9,00,00))

updater.start_polling() #recibe las actualizaciones
updater.idle()  #Se queda escuchando hast a que se cierra el programa

