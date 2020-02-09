#! /usr/bin/python
# -*- coding:utf-8 -*-

from flask import Flask, request, make_response, render_template, redirect, url_for
import requests
import json
from requests.auth import HTTPBasicAuth
import sys
import zeep

app = Flask(__name__)

def printer(msg):
    return print(msg, file=sys.stderr)

# Affiche le template contenant le formulaire
@app.route('/')
def index():
    return render_template('index.html')


# Recupère le formulaire
@app.route('/get_form', methods=['POST'])
def get_form():
    if request.method == 'POST':
        print('_________________________________________________', file=sys.stderr)
        printer('trainfrom = ' + request.form['trainfrom'])
        printer('trainto = ' + request.form['trainto'],)
        printer('traindatetime = ' + request.form['traindatetime'])
        return redirect(url_for('request_json', tfrom=request.form['trainfrom'], tto=request.form['trainto'],
                                tdatetime=request.form['traindatetime'], tcurrency=request.form['traincurrency']))
    else:
        return redirect(url_for('index'))


@app.route('/json')
@app.route('/json/<tfrom>/<tto>/<tdatetime>/<tcurrency>')
def request_json(tfrom="admin:fr:75056", tto="admin:fr:69123", tdatetime="20200116T095127", tcurrency='EUR'):
    apiKey = 'ac20e3f0-10a2-4f4e-a433-ca6b9f0cebdb'

    # On effectue un GET avec des paramètres sur l'API SNCF
    printer('_________________________________________________')
    printer('tfrom = ' + tfrom)
    printer('tto = ' + tto)
    printer('tdatetime = ' + tdatetime)
    r = requests.get(
        'https://api.sncf.com/v1/coverage/sncf/journeys?from=' + tfrom + '&to=' + tto + '&datetime= ' + tdatetime,
        auth=HTTPBasicAuth(apiKey, ''), verify=True)
    data = r.json()

    printer('__________________Contenu du JSON_________________')
    printer('obj : ' + str(data['links']))
    latDepart = str(data['journeys'][0]['sections'][0]['from']['administrative_region']['coord']['lat'])
    lonDepart = str(data['journeys'][0]['sections'][0]['from']['administrative_region']['coord']['lon'])

    printer('latitute de depart  :  ' + latDepart)
    printer('longitude de depart  :  ' + lonDepart)

    # on instancie le client SOAP
    client = zeep.Client('http://localhost:8080/Distance/soap/description')
    distance = round(client.service.calcul_distance(latDepart, 45.760585, lonDepart, 4.859435) / 1000, 2)
    printer('_______________Reponse du service SOAP_____________')
    printer('result :' + str(distance))
    """
    # On effectue un GET avec des paramètres sur notre API REST
    r1 = requests.get('http://localhost:5001/price/' + tcurrency + '/' + str(distance))
    data1 = r1.json()
    totalprice = round(data1['total'], 2)
    print('prix  :  ' + str(totalprice), file=sys.stderr)
    """
    reponse = make_response(data)
    #on précise le MIMEtype de la réponse
    reponse.mimetype = "application/json"
    return reponse
   # return render_template('result.html', la_distance = distance, le_cout = totalprice, la_monnaie = tcurrency)


if __name__ == '__main__':
    app.run(debug=True)
