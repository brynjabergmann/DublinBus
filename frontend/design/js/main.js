// Global variables
var map;
var directionsService; // Find directions from a to b
var directionsDisplay; // Displays route on map
var fromPlace = {}; 
var toPlace = {};
var routeOneTotalTravelTime;
var routeTwoTotalTravelTime;
var routeThreeTotalTravelTime;


// Map reference: https://developers.google.com/maps/documentation/javascript/adding-a-google-map
// Direction reference: https://developers.google.com/maps/documentation/javascript/examples/directions-simple

// Function that initialize and adds the map to the website
function initMap() {
    var Dublin = {lat: 53.350140, lng: -6.266155}
    directionsService = new google.maps.DirectionsService;
    directionsDisplay = new google.maps.DirectionsRenderer;
    map = new google.maps.Map(                      
        document.getElementById("map"), {zoom: 12, center: Dublin, mapTypeControl: false});
    directionsDisplay.setMap(map);                  // Connect route display to map
}


// Function that gets the date and time and turns it around 
function getInputDateAsDateObject(){
    var date = $("#datepicker input").val();  
    var time = $("#timePicker").val();
    var dateArray = date.split("/");
    // JavaScript needs date objects to have format yyyy/mm/dd hh:mm
    return new Date(`${dateArray[2]}/${dateArray[1]}/${dateArray[0]} ${time}`);
}


// Function that adds the date and time to one timestamp
function timeStamp() {
    return timestamp = Math.floor(getInputDateAsDateObject() / 1000);
}


  // Direction reference: https://developers.google.com/maps/documentation/javascript/examples/directions-simple
  // Function that calculates and displays routes
  function calculateAndDisplayRoute(directionsService, directionsDisplay) {
    var date = getInputDateAsDateObject();
    directionsService.route({
      origin: document.getElementById("fromStation").value,
      destination: document.getElementById("toStation").value,
      travelMode: "TRANSIT", 
      provideRouteAlternatives: true,
      transitOptions: {
        modes: ["BUS"],
        departureTime: date,
        routingPreference: "FEWER_TRANSFERS"    // Minimizes the number of buses for one journey
      }
    }, 
    // Callback function for route
    function(response, status) {     
      if (status === "OK") {

        // Shows max three suggested routes/result boxes
        var number_of_bus_routes = 3;
        if (response.routes.length < 3) {
            number_of_bus_routes = response.routes.length;
        }

        // Hide unused result boxes
        for (var i = 3; i > number_of_bus_routes; i--) {
            // $(`route-${i - 1}`).hide();            
        }

        // Create and display prediction for every route
        for (var i = 0; i < number_of_bus_routes; i++) {
            
            $(`#route-${i}`).empty();               // Remove old suggested data
            $(`#routeDetails_${i}`).empty();       // Remove old suggested data

            // Display images for steps (walking or bus)
            for(let j = 0; j < response.routes[i].legs[0].steps.length; j++)
            {
                const buttonWalking = `<img class="img-responsive resultImages" img src="./img/walking.png">`;
                const nextImage = `<span id="next" class="glyphicon glyphicon-chevron-right"></span>`;
                if(response.routes[i].legs[0].steps[j].travel_mode == "TRANSIT")
                {
                    const buttonBus = `<img class="img-responsive resultImages busImage" img src="./img/bus.png">
                        <h5 class="busName">[${response.routes[i].legs["0"].steps[j].transit.line.short_name}]</h5>`
                    $(`#route-${i}`).append(buttonBus);
                }
                else{
                    $(`#route-${i}`).append(buttonWalking);
                }
                if(+j + 1 !== response.routes[i].legs[0].steps.length)      // +j to ensure j is treated as number
                {
                    $(`#route-${i}`).append(nextImage);
                }
            }
            let postBody = [];
            for(let j = 0; j < response.routes[i].legs[0].steps.length; j++)
            {
                if(response.routes[i].legs[0].steps[j].travel_mode == "TRANSIT")
                {
                    let timestamp = timeStamp();
                    let start_lat = response.routes[i].legs["0"].steps[j].start_location.lat();
                    let start_long = response.routes[i].legs["0"].steps[j].start_location.lng();
                    let end_lat = response.routes[i].legs["0"].steps[j].end_location.lat();
                    let end_long = response.routes[i].legs["0"].steps[j].end_location.lng();
                    
                    let busName = response.routes[i].legs["0"].steps[j].transit.line.short_name;
                    let firstStopLocation = [start_lat, start_long];
                    let lastStopLocation = [end_lat, end_long]; 
                    let item = {
                        "firstStop": firstStopLocation,
                        "lastStop": lastStopLocation,
                        "busRoute": busName,
                        "timestamp": timestamp
                    };
                    postBody.push(item);
                }
            }
            const jsonString= JSON.stringify(postBody);
            
            if(i === 0)
            {
                routeOneTotalTravelTime = 0;
            }
            if(i === 1)
            {
                routeTwoTotalTravelTime = 0;
            }
            if(i === 2)
            {
                routeThreeTotalTravelTime = 0;
            }
            predictRoute(response, jsonString, i, postBody);
        }
        directionsDisplay.setDirections(response);
      } 
      else {
        console.log("Directions request failed due to " + status);
      }
    });
  }

function predictRoute(response, jsonString, i, postBody){
    $.post("https://dublinbus.icu/api/location_prediction_endpoint", jsonString, function(backendResponse) {
        for(let j = 0; j < response.routes[i].legs[0].steps.length; j++)
        {
            if(response.routes[i].legs[0].steps[j].travel_mode === "TRANSIT")
            {
                let predictedTime = backendResponse["predictions"].shift();
                if(i === 0)
                {
                    routeOneTotalTravelTime += +predictedTime;
                }
                if(i === 1)
                {
                    routeTwoTotalTravelTime += +predictedTime;
                }
                if(i === 2)
                {
                    routeThreeTotalTravelTime += +predictedTime;
                }
                const detailBus = `<img class="img-responsive resultImages busImage" img src="./img/bus.png"> <h5 class="displayResultsMin" id="predictionMin_${i}_${j}">${predictedTime} mins</h5>`;
                // Add element to html
                $(`#routeDetails_${i}`).append(detailBus);        
            }
            else {
                const walkingMinutes = `<img class="img-responsive resultImages walkImage" img src="./img/walking.png"><h5 class="displayResultsMin">${[response.routes[i].legs["0"].steps[j].duration.text]}</h5>`;
                $(`#routeDetails_${i}`).append(walkingMinutes);
                if(i === 0)
                {
                    routeOneTotalTravelTime += +parseInt(response.routes[i].legs["0"].steps[j].duration.text.replace("mins", "").replace(" ", ""));
                }
                if(i === 1)
                {
                    routeTwoTotalTravelTime += +parseInt(response.routes[i].legs["0"].steps[j].duration.text.replace("mins", "").replace(" ", ""));
                }
                if(i === 2)
                {
                    routeThreeTotalTravelTime += +parseInt(response.routes[i].legs["0"].steps[j].duration.text.replace("mins", "").replace(" ", ""));
                }
            }
        }
        let leapPrice = 0;
        let cashPrice = 0;
        for(let j = 0; j < backendResponse.fares.length; j++){
            leapPrice += +backendResponse.fares[j]["leap"]; //-j if 1 euro cheaper in the next bus;
            cashPrice += +backendResponse.fares[j]["cash"];
        }
        
        let price = `<h6 class="pricing">Leap: <span class="glyphicon glyphicon-euro">${leapPrice}</span> Cash: <span class="glyphicon glyphicon-euro">${cashPrice}</span></h6>`;
        $(`#route-${i}`).append(price);
        $(".sidebarPageOne").hide();
        $(".sidebarPageTwo").show();
        })
        // When response is ready
        .done(function(data) {
            updateTotalTravelTime(i);
            makeChart(postBody, response.routes[i].legs[0].steps, i);
        })
}

function updateTotalTravelTime(i){
    const travelTimeText = "Total Travel Time:";
    if(i === 0)
    {
        let totalTravelTime = `<h5>${travelTimeText} ${routeOneTotalTravelTime} minutes</h5>`
        $(`#route-${i}`).prepend(totalTravelTime);
    }
    if(i === 1)
    {
        let totalTravelTime = `<h5>${travelTimeText} ${routeTwoTotalTravelTime} minutes</h5>`
        $(`#route-${i}`).prepend(totalTravelTime);
    }
    if(i === 2)
    {
        let totalTravelTime = `<h5>${travelTimeText} ${routeThreeTotalTravelTime} minutes</h5>`
        $(`#route-${i}`).prepend(totalTravelTime);
    }
}

function makeChart(postBody, steps, routeIndex){
    let body = new Object();
    body.itinerary = new Object();
    for(let i = 0; i < postBody.length; i++)
    {
        let route = new Object();
        route.stops = [postBody[i].firstStop, postBody[i].lastStop];
        const busName = postBody[i].busRoute;
        body.itinerary[busName] = route;
    }

    let walking = 0;
    for(let i = 0; i < steps.length; i++){
        if(steps[i].travel_mode != "TRANSIT")
        {
            walking += parseInt(steps[i].duration.text.replace("mins", "").replace(" ", ""));
        }
    }
    body.walk = walking;
    body.timestamp = timeStamp();
    const jsonString = JSON.stringify(body);
    let graph = `<div class="row"><div id="chart_div_${routeIndex}" style="height: 200px; width: 300px;"></div></div>`;
    $(`#routeDetails_${routeIndex}`).append(graph);
    $.post("https://dublinbus.icu/api/chart", jsonString, function(backendResponse) {
        drawChart(backendResponse["chart"], `chart_div_${routeIndex}`);
    });
}

function drawChart(predictions, containerID) {
	let data = new google.visualization.DataTable();
	data.addColumn("string", "Hour");
    data.addColumn("number", "Minutes");
	data.addColumn({role: "style", type: "string"});
	let i;	
    let now = getInputDateAsDateObject().getHours(); 
    // hourNow - 5;
	let zone;
	let color;
	for (i = 0; i < 19; i++) {
		time = (i + 5) % 24;
		if(time == 0)
			time = "12"
		if(i < 7)
			zone = "AM";
		else
			zone = "PM";
		if(i == now)
			color = "#6699FF";
		else
			color = "silver";
		data.addRow([time.toString(), predictions[i], "color: " + color+ ";"]);

		};

    let options = {
        animation: {
            duration: 2000,
            easing: "out",
            startup: true
        },
        title: "Hourly Journey Travel Times",
        axisTitlesPosition: "out",
        backgroundColor: "transparent",
        curveType: "function",
        hAxis: {
            title: "Time of Day"
        },
        legend: {
            position: "none"
        },
        vAxis: {
			viewWindowMode: "maximized",
            format: "decimal",
            title: "\nJourney Time (mins)",
            gridlines: {
                color: "transparent"
            }
        }
    };
    let chart = new google.visualization.ColumnChart(document.getElementById(containerID));
    chart.draw(data, options);
}








  //Reference: https://github.com/rodaine/jQuery-Geolocation/blob/master/demo.html

  // Function to get the users geo location
  function getLocation($button){           
    var startCB = function() {   // CB = callback   
        $button
            .attr("disabled", "disabled"); 
    }
    var finishCB = function() {     
        $button
            .removeAttr("disabled"); 
    }
    var errorCB = function(error) { 
        console.log( "Error " + error.code + ":" + error.message ); 
    }
    var successCB = function(p) {
        var location = "Latitude: " + p.coords.latitude + "<br/>" + "Longitude: " + p.coords.longitude;
        var yourLocation = {lat: p.coords.latitude, lng: p.coords.longitude}
        var marker = new google.maps.Marker({
            position: yourLocation, 
            map: map,
            draggable: true,
            animation: google.maps.Animation.DROP
        });
        marker.addListener("click", toggleBounce);
            if (this.id == "findLocationFrom") {
                geoAddress(yourLocation, "#fromStation", true);
            }
            else {
                geoAddress(yourLocation, "#toStation", false);
            }
            
            
        // Reference: https://developers.google.com/maps/documentation/javascript/examples/marker-animations
        // Function that makes the marker bounce on the map
        function toggleBounce() {
            if (marker.getAnimation() !== null) {
              marker.setAnimation(null);
            } 
            else {
              marker.setAnimation(google.maps.Animation.BOUNCE);
            }
          }
    }
    // Configuring callbacks
    $button.geolocate({
        onStart: startCB,
        onFinish: finishCB,
        onError: errorCB,
        onSuccess: successCB,
        timeout: 5000           // If function takes more than 5 sec it will time out
    });
};



// Goecoding reference: https://developers.google.com/maps/documentation/javascript/examples/geocoding-reverse

// Function to get the address for the users location
function geoAddress(location, inputID, isFromPlace){
    if (isFromPlace) {          // isFromPlace is a boolean variable
        fromPlace = location;   // Location set to From input
    }
    else {
        toPlace = location;     // Location set to To input
    }
    var geocoder = new google.maps.Geocoder();
    geocoder.geocode({"location": location}, function(results, status){
        if (status == "OK") {
            if (results[0]) {
                try {
                    var route = results[0]["address_components"].find(function(element){            // Gets street name
                        return element.types.includes("route");})["long_name"];
                    var postalcode = results[0]["address_components"].find(function(element){       // Gets postal code
                        return element.types.includes("postal_town");})["long_name"];
                    var country = results[0]["address_components"].find(function(element){          // Gets country 
                        return element.types.includes("country", "political");})["long_name"];
                    $(inputID).val(`${route}, ${postalcode}, ${country}`);
                }
                catch{
                        alert("Unable to find your location. Please insert address manually.");
                }
            }
        }
    });
}



// Reference: https://developers.google.com/maps/documentation/javascript/places-autocomplete
function autocomplete(){
    var inputFrom = document.getElementById("fromStation");
    var inputTo = document.getElementById("toStation");

    function addAutocomplete(input, fromOrTo) {
        var autocomplete = new google.maps.places.Autocomplete(input);

        autocomplete.bindTo("bounds", map);
        autocomplete.setTypes(["address"]);
        autocomplete.setFields(         // Set the data fields to return when the user selects a place.
            ["address_components", "geometry"]);
        autocomplete.setOptions({strictBounds: true});
        autocomplete.addListener("place_changed", function() {
            var place = autocomplete.getPlace();
            if(fromOrTo === "fromPlace"){
                fromPlace.lat = place.geometry.location.lat();
                fromPlace.lng = place.geometry.location.lng();
            } else{
                toPlace.lat = place.geometry.location.lat();
                toPlace.lng = place.geometry.location.lng();
            }
            var address = "";
            if (place.address_components) {
                address = [
                (place.address_components[0] && place.address_components[0].short_name || ""),
                (place.address_components[1] && place.address_components[1].short_name || ""),
                (place.address_components[2] && place.address_components[2].short_name || "")
                ].join(" ");
            }
        });
    }
    
    addAutocomplete(inputFrom, "fromPlace");
    addAutocomplete(inputTo, "toPlace");
}

function fetchWeather(){
    fetch("https://dublinbus.icu/api/current_weather")   // First make a GET request to our endpoint
        .then(function(rawResponse){                    // Once that raw response is received, do something with it,
            return rawResponse.json();                  // in this case, take the string response and convert to a JSON object
        })
        .then(function(weatherJSON){
            // Round the temp to the nearest integer
            document.getElementById("weatherTemp").innerHTML = `${Math.round(weatherJSON["temp"]).toString()}°C`;

            //remove later
            tempNow = weatherJSON["temp"];
            rainNow = weatherJSON["precip_intensity"];

            $(".icon").attr("id", weatherJSON["icon"]);
            weatherIcons();
        })
        .catch(function(){
            $(".icon").attr("id", "partly-cloudy-day");
            weatherIcons();
        });
}


//Function for the weather icons. Reference: https://github.com/darkskyapp/skycons
function weatherIcons(){
    var icons = new Skycons(),
            list  = [
                "clear-day", "clear-night", "partly-cloudy-day",
                "partly-cloudy-night", "cloudy", "rain", "sleet", "snow", "wind",
                "fog"  ],
            i;
        for(i = list.length; i--; )
            icons.set(list[i], list[i]);
        icons.play();
}

function updateDropDown(element){
    // Reference: https://stackoverflow.com/questions/8482241/selecting-next-input
        $("#Bus").val(element.target.innerText);  
}

function searchForRoute(){         // Function for the search button (what happens after the user clicks on "Search")
    calculateAndDisplayRoute(directionsService, directionsDisplay);
}

// Function for the date picker
function setInitialDateTime(){
    const date = new Date();
    $("#datepicker input").val(`${date.getDate()}/${date.getMonth() + 1}/${date.getFullYear()}`);
}

// Function for the clock picker
function setInitialClock(){
    const time = new Date();
    if(+time.getMinutes() < +10)
    {
        $("#timePicker").val(`${time.getHours()}:0${time.getMinutes()}`);    
    }
    else{
        $("#timePicker").val(`${time.getHours()}:${time.getMinutes()}`);
    }
}


function createMarker(location) {
    var marker = new google.maps.Marker({
        position: location, 
        map: map,
        draggable: true,
        animation: google.maps.Animation.DROP
    });
}


$(window).on("load", function(){

    $(".clockpicker").clockpicker({
        donetext: "",
        autoclose: true
    });
    $( "#datepicker" ).datepicker({
        autoclose: true,
        format: "dd/mm/yyyy",
        startDate: "1d"
    });
    setInitialDateTime();
    setInitialClock();
    fetchWeather();
    getLocation($("#findLocationFrom"));
    getLocation($("#findLocationTo"));
    autocomplete();
    $("#searchButton").on("click", searchForRoute);
    $(".suggestedRoute").on("click", function(e){
        if (e.target.id == "route-0") {
            directionsDisplay.setRouteIndex(0);
        }
        if (e.target.id == "route-1") {
            directionsDisplay.setRouteIndex(1);
        }
        if (e.target.id == "route-2") {
            directionsDisplay.setRouteIndex(2);
        }
    });
    $("#backToPageOne").on("click", function(){
       $(".sidebarPageOne").show();
       $(".search").show();
       $(".sidebarPageTwo").hide();
    });


    google.charts.load("current", {
        "packages": ["corechart"]
    });

});
