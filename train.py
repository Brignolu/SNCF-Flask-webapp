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
    return render_template('index.html')


# Recupère les formulaires
@app.route('/get_form', methods=['POST'])
def get_form():
    if request.method == 'POST':
        
        """
        #DEBUG
        #Ici on affiche les données des formulaires
        printer('trainfrom = ' + request.form['trainfrom'])
        printer('trainto = ' + request.form['trainto'],)
        printer('traindate = ' + request.form['traindate'])
        printer('traintime = ' + request.form['traintime'])
        printer('currency =' + request.form['traincurrency'])
        """
        
        #On effectue une requete a l'api sncf afin de recuperer le stop point associé a la gare en entrée
        rdepstoppoint= requests.get('https://api.sncf.com/v1/coverage/sncf/pt_objects?q='+request.form['trainfrom'] +'&', auth=HTTPBasicAuth(apiKey, ''), verify=True)
        depstoppoint = rdepstoppoint.json()
        rarrstoppoint= requests.get('https://api.sncf.com/v1/coverage/sncf/pt_objects?q='+request.form['trainto'] +'&', auth=HTTPBasicAuth(apiKey, ''), verify=True)
        arrstoppoint = rarrstoppoint.json()

        #On construit la variable datetime avec le format : YYYYMMddTHHmmss
        traindatetime = request.form['traindate'][0:4]+ request.form['traindate'][5:7] + request.form['traindate'][8:10] + 'T' + request.form['traintime'][0:2] + request.form['traintime'][3:5] + '00'
        
        """
        #DEBUG
        printer(traindatetime)
        printer(pprint.pformat(depstoppoint['pt_objects'][0]['name'] + ' : ' + depstoppoint['pt_objects'][0]['id']  + ' : ' + depstoppoint['pt_objects'][0]['stop_area']['coord']['lat']  + ' : ' + depstoppoint['pt_objects'][0]['stop_area']['coord']['lon']))
        printer(pprint.pformat(arrstoppoint['pt_objects'][0]['name'] + ' : ' + arrstoppoint['pt_objects'][0]['id'] + ' : ' + arrstoppoint['pt_objects'][0]['stop_area']['coord']['lat']  + ' : ' + arrstoppoint['pt_objects'][0]['stop_area']['coord']['lon']))
        """
        
        #On récupère les coordonées et l'identifiant du stop_point
        fromlat = depstoppoint['pt_objects'][0]['stop_area']['coord']['lat']
        fromlon = depstoppoint['pt_objects'][0]['stop_area']['coord']['lon']
        tolat = arrstoppoint['pt_objects'][0]['stop_area']['coord']['lat']
        tolon = arrstoppoint['pt_objects'][0]['stop_area']['coord']['lon']
        frompt = depstoppoint['pt_objects'][0]['id']
        topt = arrstoppoint['pt_objects'][0]['id']
        currency = request.form['traincurrency']
        
        return redirect(url_for('request_json', tfrom=frompt,tto=topt,tdatetime=traindatetime, tcurrency=currency,tfromlat = fromlat, tfromlon = fromlon,ttolat = tolat,ttolon = tolon))


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
    printer('durée totale du trajet : ' + str(totalduration))
    route =[]
    trains = []
    durations = []
    arrivals = []
    departures = []
    for i in range(0,len(data['journeys'][0]['sections'])):
        if (data['journeys'][0]['sections'][i]['type'] != 'crow_fly') and (data['journeys'][0]['sections'][i]['type'] != 'waiting') and (data['journeys'][0]['sections'][i]['type'] != 'transfer') :
            
            """
            #DEBUG
            printer(data['journeys'][0]['sections'][i]['from']['name'])
            printer(data['journeys'][0]['sections'][i]['display_informations']['commercial_mode'])
            printer(data['journeys'][0]['sections'][i]['display_informations']['headsign'])
            printer(data['journeys'][0]['sections'][i]['to']['name'])
            """
            
            route.append(data['journeys'][0]['sections'][i]['from']['name'])
            trains.append(data['journeys'][0]['sections'][i]['display_informations']['commercial_mode'] + ' n°' + data['journeys'][0]['sections'][i]['display_informations']['headsign'])
            route.append(data['journeys'][0]['sections'][i]['to']['name'])
            dur = str(time.strftime("%H:%M", time.gmtime(data['journeys'][0]['sections'][i]['duration']))) #On transforme la durée en secondes par une string en HH:mm
            durations.append(dur)
            printer(data['journeys'][0]['sections'][i]['base_departure_date_time'][9:])
            # TODO stocker les arrival_date_time et base_departure_datetime en les convertissant de YYYYTHHmmss vers une string de type HH:mm
            departures.append(pdatetimetostr(data,i,'departure_date_time'))
            arrivals.append(pdatetimetostr(data,i,'arrival_date_time'))
        elif data['journeys'][0]['sections'][i]['type'] == 'waiting':
            
            """
            #DEBUG
            printer(data['journeys'][0]['sections'][i]['type'])
            """
            dur = str(time.strftime("%H:%M", time.gmtime(data['journeys'][0]['sections'][i]['duration']))) #On transforme la durée en secondes par une string en HH:mm
            durations.append(dur)
            route.append(data['journeys'][0]['sections'][i]['type'])

    # on instancie le client SOAP
    client = zeep.Client('http://localhost:8080/Distance/soap/description')
    distance = round(client.service.calcul_distance(tfromlat, ttolat, tfromlon, ttolon) / 1000, 2)
    
    """
    #DEBUG
    printer('Distance issue de notre service SOAP :' + str(distance))
    """
    
    # On effectue une requete a notre api afin de recuperer le prix associé a la distance du trajet et la monnaie
    r1 = requests.get('http://localhost:5001/price/' + tcurrency + '/' + str(distance))
    data1 = r1.json()
    totalprice = round(data1['total'], 2)
    
    """
    #DEBUG
    printer('Prix issu de notre API REST  :  ' + str(totalprice))
    """
    
    """
    #affiche le json résultant de la requête a l'api SNCF (journeys)
    #DEBUG
    reponse = make_response(data)
    reponse.mimetype = "application/json"
    return reponse
    """
    
    return render_template('result.html', la_distance = distance, le_cout = totalprice, la_monnaie = tcurrency,la_duree_totale = totalduration, trajet = route, reftrains = trains,duree_trains = durations)


if __name__ == '__main__':
    app.run(debug=True)
