# dublinbus.icu

The team Superficial Intelligence developed dublinbus.icu
The project aims to give trip duration predictions for Dublin Bus that are more accurate than Dublin Bus’ own predictions. In order to accommodate this, Dublin Bus has been generous enough to share raw data with us that we cleaned and prepared to create a prediction model. 

## Deliverables

The link to the repository is: https://gitlab.com/nmckimm/superficial-intelligence.git

The website is hosted on https://dublinbus.icu/


## Overview

The main features of this web application are as follows:

* Dublin Bus provided us with data from 2016 and 2017 which was cleaned, prepared and loaded into a MySQL database
* Historical weather data was scraped from the Dark Sky Weather API. 
* A prediction model was created from each bus trip and using the bus data and the historical weather data
* Current and forecasted data is also scraped from the Dark Sky Weather API.
* The Google Maps API was used to display the predicted journey on our route
* A twitter script was developed and implemented that scrapes the AARoadWatch Twitter page for tweets relevant to Dublin that mention collisions or traffic disruptions, and a red translucent circle will overlay the map at a radius around this location
* There is a sidebar where the user can enter their location or use their current location. The user can then enter their destination, desired date, and desired time for their prediction
* The sidebar will then show three predictions including walking time which can be clicked on to show a chart which displays the predicted travel time on a selection of hours throughout the day
* A fare calculator was implemented on this screen too and will show you the price of your journey for cash fares and for leap card fares
* A night mode toggle has been implemented to change the map from night mode to day mode
* The walking directions from your location to your first bus stop and from your last stop to your desired destination is also displayed on the map.




### Prerequisites

This project was programmed in a Python 3.6 environment. For full requirements, please navigate to requirements.txt which can be installed using PIP.

```
This is a full stack web application. From this installation you will not have access to our database as it is password protected. 

```

### Installing

```
If you have access to the server via SSH and port forwarding, you can run “python manage.py run server” in the command line once the requirements file has been installed
```


## Deployment

The web application is deployed using Gunicorn and NGINX.



## Authors

* Brynja Halldorsdottir
* Marinana Levova
* Neil McKimm
* Peter Hanrahan



## License

This project is licensed under the MIT License - see the [LICENSE.md](LICENSE.md) file for details

