# SNCF-Flask-webapp :bullettrain_front:
A flask web-app that interrogates the navitia api to retrieve journeys and calculate the distance of the route by interrogating a homemade SOAP Service. it also interrogates an homemade REST-API to convert currencies.

# Requirements

ladon (SOAP Service), zeep (SOAP Client), flask, flask_restplus (REST Service)

## API used:

SNCF API + Foreign exchange rates API



# Setup:

### Launch SOAP Server :

```
ladon-3.7-ctl testserve SoapDistanceService.py -p 8080
```

### Launch Flask App :

```
py train.py
```

### Launch REST Service :

```
py RestService.py
```

# Crédits

I would like to thank HashtagCheminot for his beautiful Pendule.
Here's the link to his profile : https://jsfiddle.net/user/HashtagCheminot/fiddles/




# Devlog

### Liens

- https://api.navitia.io/v1/coverage/sncf/pt_objects?q=lyon&


- https://api.navitia.io/v1/coverage/sncf/journeys?to=stop_area%3AOCE%3ASA%3A87686006&from=stop_area%3AOCE%3ASA%3A87723197&datetime_represents=departure&datetime=20200221T000000&


## TODO :
- [X] Bouton réinitialiser dans les inputs de l'index qui re-enable le champ et re-initialise la value du champ.
- [X] Vue result basique
- [ ] Vue result React
- [ ] Rajouter la durée de chaque Trajet
-  [ ] Deployer sur Heroku
