from flask import Flask
from flask_restplus import Resource, Api
import requests
import sys
import pprint

app = Flask(__name__)
api = Api(app)

def printer(msg):
    return print(msg, file=sys.stderr)

@api.route('/price')
@api.route('/price/<currency>/<distance>')
class Price(Resource):
    def get(self, currency="EUR", distance="1"):
        
        #Requete à l'api exchange rates afin d'obtenir les taux de changes des différentes monnaies
        r = requests.get('https://api.exchangeratesapi.io/latest')
        data = r.json()
        
        #On defini un prix par KM 
        priceperkm = 0.3
        rates = data['rates']
        
        #DEBUG
        printer('data : ' + str(pprint.pformat(data)))

        #Si la monnaie fournie en entrée est l'euro  : on effectue pas de conversion puisque c'est la monnaie de base
        if currency == 'EUR':
            total = float(distance) * priceperkm
            return {'total': total}
        
        #On cherche le taux de change de la monnaie et on effectue la conversion
        for key, value in rates.items():
            if currency == key:
                rate = rates[key]
                total = (rate * priceperkm) * float(distance)
                return {'total': total}
        return {'error': 'please enter a valid currency'}


if __name__ == '__main__':
    app.run(debug=True, port=5001)
