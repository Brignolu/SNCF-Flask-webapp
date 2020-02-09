from flask import Flask
from flask_restplus import Resource, Api
import requests
import sys

app = Flask(__name__)
api = Api(app)


@api.route('/price')
@api.route('/price/<currency>/<distance>')
class Price(Resource):
    def get(self, currency='EUR', distance='1'):
        r = requests.get('https://api.exchangeratesapi.io/latest')
        data = r.json()
        rates = data['rates']
        print('data : ' + str(data), file=sys.stderr)
        priceperkm = 0.3
        if currency == 'EUR':
            total = float(distance) * priceperkm
            return {'currency': currency, 'total': total}
        for key, value in rates.items():
            print('key : ' + str(key), file=sys.stderr)
            if currency == key:
                rate = rates[key]
                total = (rate * priceperkm) * float(distance)
                return {'currency': currency, 'total': total}
        return {'error': 'please enter a valid currency'}


if __name__ == '__main__':
    app.run(debug=True, port=5001)
