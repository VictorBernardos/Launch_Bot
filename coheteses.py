from urllib.request import urlopen
import datetime
import json
import telegram
import time
from telegram.ext import Updater, CommandHandler, CallbackQueryHandler, MessageHandler, Filters
from telegram import InlineKeyboardButton, InlineKeyboardMarkup


cohete_emoji = u'\U0001F680'
reloj_emoji = u'\U0001F550'
no_emoji = u'\U0000274C'
si_emoji = u'\U00002705'
warning_emoji = u'\U000126A0'

url = 'https://launchlibrary.net/1.4/launch'
TOKEN = "TOKEN"


print ('Bot iniciado') 
lista=[]

#Nos permite suscribirnos a las notificaciones
def activar(bot,update):
    global lista
    bot.deleteMessage (update.message.chat.id,update.message.message_id)

    if(update.message.chat_id in lista):    #Comprobamos que esta en la lista
        bot.sendMessage(update.message.chat_id,"Ya estabas dentro de la lista")
        
    else:                                   #Si no esta lo añadimos
        bot.sendMessage(update.message.chat_id,u"Has sido correctamente agregado a la lista\nA partir de ahora recibiras notificaciones automáticas a las 9:00" + reloj_emoji)
        lista.append(update.message.chat_id)

#Nos permite dessuscribirnos a las notificaciones
def eliminar(bot,update):
    global lista
    bot.deleteMessage (update.message.chat.id,update.message.message_id)

    if(update.message.chat_id in lista):    #Si esta en la lista lo borramos
        lista.remove(update.message.chat_id)
        bot.sendMessage(update.message.chat_id,"Has sido correctamente eliminado de la lista y no recibiras notificaciones")
    else:                                   #Si no lanzamos error
         bot.sendMessage(update.message.chat_id,"Para ser eliminado de la lista, primero debes estar en ella")
    
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

#Funcion que comvierte la hora y fecha de un lanzamiento a la de españa
##REESCRIBIR FUNCION
def convertirhorario(launchId):
    tiempo = launchId['net'].split(" ")
    horas = tiempo[3].split(":")
    h = int(horas[0])
        
    #Traduccion de los meses de ingles a castellano
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
    
    #Ajuste de la hora de UTC a GTM+1 (Madrid)
    if(h==23):
        h=1             #Si son las 23 de la noche,convertimos la hora a la 1 de la mañana
        dia=int(dia)    #El dia aumenta para ello lo convertimos a entero
        dia=dia+1
    else:
        h=h+1

    
    return(str(dia) + " de " + mes + " " + tiempo[2] + " " + str(h) + ":" + horas[1] + ":" + horas[2] + ' (GTM+1)')

#Poniendo /lista nos saca la lista de lanzamientos
def launch(bot, update):
    paquete = urlopen(url)          
    datos = json.load(paquete)   
    array = datos['launches']
    data = ''
    for i in range(0,len(array)):
        data = str(cohete_emoji + '<b>' + array [len(array) - i - 1] ['name'] + '</b>\n' + reloj_emoji + '<i>' + convertirhorario(array [len(array) - i - 1]) + '</i>\n') + data
    bot.sendMessage(update.message.chat_id, data,'HTML')

#Poniendo /next nos dice el siguiente lanzamiento y el enlace para poder verlo
def siguiente(bot,update):
    paquete = urlopen(url)
    datos = json.load(paquete)  
    array = datos['launches']
    data = 'Próximo lanzamiento: \n' + str(cohete_emoji + '<b>' + array [0] ['name'] + '</b>\n' + reloj_emoji + '<i>' + convertirhorario(array[0]) + '</i>\n')
    bot.sendMessage(update.message.chat_id, data,'HTML')

    #Comprobamos si hay enlace de video disponible
    try:
        video = array [0] ['vidURLs']   

    except KeyError:
        print("No hay enlace de video")    

    else: 
        vid=video[0].split("[")
        bot.sendMessage(update.message.chat_id, vid[0])

#Envia el mensaje automatico a las personas (chatid) que tengan las notificaciones activas
def automatico(bot,chatid):
    paquete = urlopen(url)
    datos = json.load(paquete)  
    array = datos['launches']
    data = 'Próximo lanzamiento: \n' + str(cohete_emoji + '<b>' + array [0] ['name'] + '</b>\n' + reloj_emoji + '<i>' + convertirhorario(array[0]) + '</i>\n')
    bot.sendMessage(chatid, data,'HTML')

    #Comprobamos si hay enlace de video disponible
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
    #Recorremos la lista, y avisamos a cada usuario si hay lanzamiento o no.
    for i in range(0,len(lista)):
        if(hay_lanzamiento()):
            automatico(bot,lista[i])
        else:
            bot.sendMessage(lista[i], 'Hoy no hay lanzamientos')

#Mensaje de bienvenida, tambien nos deja elegir que hacer con nuestras notificiaciones
def start(bot, update):
    bot.send_message(update.message.chat_id, cohete_emoji + 'Bienvenido al BOT de lanzamientos' + cohete_emoji + '\nPodras estar al ' + u'día' + ' de todos los lanzamientos')

    button_notis (bot, update) #Sacamos los botones para elegir


#Imprime los botones para consultar y modificar el estado de tus notificaciones
def button_notis (bot, update):
    global lista
    
    if(update.message.chat_id in lista):
        data = si_emoji + 'ACTIVADO'
        #bot.sendMessage(update.message.chat_id, si_emoji + 'Activadas')
    else:
        data = no_emoji + 'DESACTIVADO'
        #bot.sendMessage(update.message.chat_id, no_emoji + 'Desactivadas')

    bot.sendMessage(update.message.chat_id, 'El estado actual de las notificaciones diarias es: ' + data)

    keyboard = [[InlineKeyboardButton(si_emoji +"Activar", callback_data='notis_on'),
                 InlineKeyboardButton(no_emoji + "Desactivar", callback_data='notis_off')]]

    reply_markup = InlineKeyboardMarkup(keyboard)
    update.message.reply_text('¿Que desea hacer?',reply_markup=reply_markup)

#Comprobamos las lecturas de los botones
def button(bot, update):
    query = update.callback_query
    text =query.data
    if text == 'notis_on':
        activar(bot,update.callback_query)
    elif text == 'notis_off':
        eliminar(bot,update.callback_query)
    else:
        print ("error")

updater = Updater(TOKEN, workers=200)

updater.dispatcher.add_handler(CommandHandler('start', start))
updater.dispatcher.add_handler(CommandHandler('lista', launch))
updater.dispatcher.add_handler(CommandHandler('next', siguiente))
updater.dispatcher.add_handler(CommandHandler('notificaciones', button_notis))

updater.dispatcher.add_handler(CallbackQueryHandler(button))


#Funcion que se usa para pruebas
#updater.dispatcher.add_handler(CommandHandler('debug', debug))

#Job para la automación de las notificaciones a una hora prefijada
job = updater.job_queue
job.run_daily(callback_auto, time=datetime.time(9,00,00))

updater.start_polling() #recibe las actualizaciones
updater.idle()  #Se queda escuchando hast a que se cierra el programa
