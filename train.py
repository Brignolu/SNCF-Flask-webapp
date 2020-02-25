#! /usr/bin/python
# -*- coding:utf-8 -*-

from flask import Flask, request, make_response, render_template, redirect, url_for
import requests
import json
from requests.auth import HTTPBasicAuth
import sys
import zeep
import pprint
import time

app = Flask(__name__)

apiKey = 'ac20e3f0-10a2-4f4e-a433-ca6b9f0cebdb'

def printer(msg):
    return print(msg, file=sys.stderr)

def pdatetimetostr(data,index_sections, field):
    return data['journeys'][0]['sections'][index_sections][field][9:11] + ':' + data['journeys'][0]['sections'][index_sections][field][11:13]

# Affiche le template contenant le formulaire
@app.route('/')
def index():
    
    """
    #DEBUG
    printer("Bienvenue dans Trouve ton Train")
    """
    
    return render_template('index.html')


# Recupère les formulaires
@app.route('/get_form', methods=['GET', 'POST'])
def get_form():
    if request.method == 'POST':

        """
        #DEBUG
        #Ici on affiche les données des formulaires
        printer('trainfrom = ' + request.form['trainfrom']) # Ici juste pour information
        printer('trainto = ' + request.form['trainto'])  # Ici juste pour information
        printer('traindate = ' + request.form['traindate'])
        printer('traintime = ' + request.form['traintime'])
        printer('currency =' + request.form['traincurrency'])
        """  

        #On recupère le Json résultant de la requete a l'API SNCF depuis un champ hidden
        depstoppoint = json.loads(request.form['fromdata'])
        arrstoppoint = json.loads(request.form['todata'])

        #On construit la variable datetime avec le format : YYYYMMddTHHmmss
        traindatetime = request.form['traindate'][0:4]+ request.form['traindate'][5:7] + request.form['traindate'][8:10] + 'T' + request.form['traintime'][0:2] + request.form['traintime'][3:5] + '00'
        

        #On récupère les coordonées et l'identifiant du stop_point
        fromlat = depstoppoint['stop_area']['coord']['lat']
        fromlon = depstoppoint['stop_area']['coord']['lon']
        tolat = arrstoppoint['stop_area']['coord']['lat']
        tolon = arrstoppoint['stop_area']['coord']['lon']
        frompt = depstoppoint['id']
        topt = arrstoppoint['id']
        currency = request.form['traincurrency']
        return redirect(url_for('request_json', tfrom=frompt, tto=topt, tdatetime=traindatetime, tcurrency=currency, tfromlat = fromlat, tfromlon = fromlon, ttolat = tolat, ttolon = tolon))
    else:
        return "ERROR : NOT A POST REQUEST"


@app.route('/json')
@app.route('/json/<tfrom>/<tto>/<tdatetime>/<tcurrency>/<tfromlat>/<tfromlon>/<ttolat>/<ttolon>')
def request_json(tfrom="admin:fr:75056", tto="admin:fr:69123", tdatetime="20200216T095127", tcurrency='EUR',tfromlat = "0",tfromlon="0",ttolat = "0",ttolon="0"):

    """
    #DEBUG
    printer('tfrom = ' + tfrom)
    printer('tfromlat = ' + tfromlat)
    printer('tto = ' + tto)
    printer('tdatetime = ' + tdatetime)
    """

    
    # On effectue une requete a l'api sncf afin de recuperer les trajets associés aux 2 stop point et la date
    r = requests.get('https://api.sncf.com/v1/coverage/sncf/journeys?from=' + tfrom + '&to=' + tto + '&datetime_represents=departure&datetime= ' + tdatetime, auth=HTTPBasicAuth(apiKey, ''), verify=True)
    data = r.json()
    totalduration = time.strftime("%H:%M", time.gmtime( data['journeys'][0]['duration']))
    """
    #DEBUG
    printer('durée totale du trajet : ' + str(totalduration))
    """
    
    route =[]
    for i in range(0,len(data['journeys'][0]['sections'])):
        if (data['journeys'][0]['sections'][i]['type'] != 'crow_fly') and (data['journeys'][0]['sections'][i]['type'] != 'waiting') and (data['journeys'][0]['sections'][i]['type'] != 'transfer') :
            
            """
            #DEBUG
            printer(data['journeys'][0]['sections'][i]['from']['name'])
            printer(data['journeys'][0]['sections'][i]['display_informations']['commercial_mode'])
            printer(data['journeys'][0]['sections'][i]['display_informations']['headsign'])
            printer(data['journeys'][0]['sections'][i]['to']['name'])
            """
            
            train_str = data['journeys'][0]['sections'][i]['display_informations']['commercial_mode'] + ' n°' + data['journeys'][0]['sections'][i]['display_informations']['headsign']
            dur = str(time.strftime("%H:%M", time.gmtime(data['journeys'][0]['sections'][i]['duration']))) #On transforme la durée en secondes par une string en HH:mm

            """
            #DEBUG
            printer((data['journeys'][0]['sections'][i]['from']['name'], data['journeys'][0]['sections'][i]['to']['name'], train_str, dur, pdatetimetostr(data, i, 'departure_date_time'), pdatetimetostr(data, i, 'arrival_date_time')))
            """
            
            route.append((data['journeys'][0]['sections'][i]['from']['name'], data['journeys'][0]['sections'][i]['to']['name'], train_str, dur, pdatetimetostr(data, i, 'departure_date_time'), pdatetimetostr(data, i, 'arrival_date_time')))

            
        elif data['journeys'][0]['sections'][i]['type'] == 'waiting':
            
            """
            #DEBUG
            printer(data['journeys'][0]['sections'][i]['type'])
            """
            
            dur = str(time.strftime("%H:%M", time.gmtime(data['journeys'][0]['sections'][i]['duration']))) #On transforme la durée en secondes par une string en HH:mm

            """
            #DEBUG
            printer((data['journeys'][0]['sections'][i]['type'], ' ' , ' ', dur, ' ', ' '))
            """
            
            route.append((data['journeys'][0]['sections'][i]['type'], ' ' , ' ', dur, ' ', ' '))
    
    # on instancie le client SOAP
    client = zeep.Client('http://trouvetontrain.herokuapp.com/soapservice/Distance/soap/description')
    distance = round(client.service.calcul_distance(tfromlat, ttolat, tfromlon, ttolon) / 1000, 2)
    
    """
    #DEBUG
    printer('Distance issue de notre service SOAP :' + str(distance))
    """
    
    # On effectue une requete a notre api afin de recuperer le prix associé a la distance du trajet et la monnaie
    r1 = requests.get('http://trouvetontrain.herokuapp.com/restservice/price/' + tcurrency + '/' + str(distance))
    data1 = r1.json()
    totalprice = round(data1['total'], 2)
    
    
    """
    #DEBUG
    printer('Prix issu de notre API REST  :  ' + str(totalprice))
    """
    
    """
    #DEBUG
    #affiche le json résultant de la requête a l'api SNCF (journeys)
    reponse = make_response(data)
    reponse.mimetype = "application/json"
    return reponse
    """
    
    return render_template('result.html', la_distance = distance, le_cout = totalprice, la_monnaie = tcurrency,la_duree_totale = totalduration, trajet = route)



if __name__ == '__main__':
    app.run(debug=True)
