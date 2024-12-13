# SNCF-Flask-webapp :bullettrain_front:
A flask web-app that interrogates the navitia REST-API to retrieve journeys. It calculates the distance of the route by interrogating a homemade SOAP Service. It also interrogates a homemade REST-API to convert currencies.

![Index Capture](indexcapture.png)
![Result Capture](resultcapture.png)

# Requirements

ladon (SOAP Service), zeep (SOAP Client), flask, flask_restplus (REST Service)

```
pip install -r requirements.txt
```

## APIs used

SNCF API + Foreign exchange rates API



# Setup

### Launch :

```
python dispatcher.py
```

# Credits

I would like to thank HashtagCheminot for his beautiful Pendule.
Here's the link to his profile : https://jsfiddle.net/user/HashtagCheminot/fiddles/
