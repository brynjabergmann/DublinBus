// Global variables
var map;
var directionsService; // Find directions from a to b
var directionsDisplay; // Displays route on map
var fromPlace = {}; 
var toPlace = {};



// Map reference: https://developers.google.com/maps/documentation/javascript/adding-a-google-map
// Direction reference: https://developers.google.com/maps/documentation/javascript/examples/directions-simple

// Function that initialize and adds the map to the website
function initMap() {                                
    var Dublin = {lat: 53.350140, lng: -6.266155}
    directionsService = new google.maps.DirectionsService;
    directionsDisplay = new google.maps.DirectionsRenderer;
    map = new google.maps.Map(                      
        document.getElementById('map'), {zoom: 12, center: Dublin});
    directionsDisplay.setMap(map);                  // Connect route display to map
    console.log(directionsDisplay);
    console.log(directionsDisplay.routes)
  }

 

// Function that gets the date and time and turns it around 
function getInputDateAsDateObject(){
    var date = $("#datepicker input").val();  
    var time = $("#timePicker").val();
    var dateArray = date.split("/");
    // JavaScript needs date objects to have format yyyy/mm/dd hh:mm
    return new Date(`${dateArray[2]}/${dateArray[1]}/${dateArray[0]} ${time}`);
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
        routingPreference: "FEWER_TRANSFERS"
      }
    }, 

    // Callback function for route
    function(response, status) {     
      if (status === 'OK') {
        console.log(response);

        var object = new Object();
        object.day = date.getDay();
        object.hour = date.getHours();
        object.temp = tempNow;
        object.rain = rainNow;
        object.route = response.routes["0"].legs["0"].steps[1].transit.line.short_name;

        object.From = { 
            Lat: response.routes["0"].legs["0"].steps[1].start_location.lat(),
            Lng: response.routes["0"].legs["0"].steps[1].start_location.lng()
        }
        object.To = {
            Lat: response.routes["0"].legs["0"].steps[1].end_location.lat(),
            Lng: response.routes["0"].legs["0"].steps[1].end_location.lng()
        }
        object.Date  = $("#datepicker input").val();
        object.Time = $("#timePicker").val();
        const jsonString= JSON.stringify(object);
        console.log(jsonString);

         // Send data to api
        $.post("http://127.0.0.1:8000/api/make_prediction_using_coordinates", jsonString, function(response) {
            console.log( "success" );
            console.log("response: " + response);
            console.log(response);
            
            $("#prediciton").text(`Predicted travel time: ${response["result"]} minutes`);
        })
        // When response is ready
        .done(function() {
            console.log( "Display prediction to user" );
        })
        // Api failure
        .fail(function() {
            $("#prediciton").text(`Predicted travel time: ${16} minutes`);
            console.log( "error" );
        })
        // Always run
        .always(function() {
            console.log( "finished" );
        });

        // The first 4 bus routes
        console.log(response.routes["0"].legs["0"].steps[1].transit.line.short_name);
        console.log(response.routes["1"].legs["0"].steps[1].transit.line.short_name);
        console.log(response.routes["2"].legs["0"].steps[1].transit.line.short_name);
        console.log(response.routes["3"].legs["0"].steps[1].transit.line.short_name);
        // The lat and long for the origin bus stop
        console.log(response.routes["0"].legs["0"].steps[1].start_location.lat());
        console.log(response.routes["0"].legs["0"].steps[1].start_location.lng());
        // The lat and long for the destination bus stop (if only one bus)
        console.log(response.routes["0"].legs["0"].steps[1].end_location.lat());
        console.log(response.routes["0"].legs["0"].steps[1].end_location.lng());
        // The lat and long for the destination bus stop (if two buses)
        console.log(response.routes["0"].legs["0"].steps[2].end_location.lat());
        console.log(response.routes["0"].legs["0"].steps[2].end_location.lng());
        
        directionsDisplay.setDirections(response);
      } 
      else {
        console.log("Directions request failed due to " + status);
      }
    });
  }



  //Reference: https://github.com/rodaine/jQuery-Geolocation/blob/master/demo.html

  // Function to get the users geo location
  function getLocation($button){           
    var startCB = function() {   // CB = callback   
        $button
            .attr('disabled', 'disabled'); 
    }
    var finishCB = function() {     
        $button
            .removeAttr('disabled'); 
    }
    var errorCB = function(error) { 
        console.log( 'Error ' + error.code + ':' + error.message ); 
    }
    var successCB = function(p) {
        var location = 'Latitude: ' + p.coords.latitude + '<br/>' + 'Longitude: ' + p.coords.longitude;
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
    geocoder.geocode({'location': location}, function(results, status){
        if (status == 'OK') {
            if (results[0]) {
                var route = results[0]["address_components"].find(function(element){            // Gets street name
                    return element.types.includes("route");})["long_name"];
                var postalcode = results[0]["address_components"].find(function(element){       // Gets postal code
                    return element.types.includes("postal_town");})["long_name"];
                var country = results[0]["address_components"].find(function(element){          // Gets country 
                    return element.types.includes("country", "political");})["long_name"];
                $(inputID).val(`${route}, ${postalcode}, ${country}`);
            }
        }
    });
}



// Reference: https://developers.google.com/maps/documentation/javascript/places-autocomplete
function autocomplete(){
    // var input = $('#fromStation');
    var inputFrom = document.getElementById('fromStation');
    var inputTo = document.getElementById('toStation');

    function addAutocomplete(input, fromOrTo) {
        var autocomplete = new google.maps.places.Autocomplete(input);
        // Bind the map's bounds (viewport) property to the autocomplete object,
            // so that the autocomplete requests use the current map bounds for the
            // bounds option in the request.
            autocomplete.bindTo('bounds', map);
            autocomplete.setTypes(['address']);
            // Set the data fields to return when the user selects a place.
            autocomplete.setFields(
                ['address_components', 'geometry']);
            autocomplete.addListener('place_changed', function() {
                var place = autocomplete.getPlace();
                if(fromOrTo === "fromPlace"){
                    fromPlace.lat = place.geometry.location.lat();
                    fromPlace.lng = place.geometry.location.lng();
                } else{
                    toPlace.lat = place.geometry.location.lat();
                    toPlace.lng = place.geometry.location.lng();
                }
                var address = '';
                if (place.address_components) {
                    address = [
                    (place.address_components[0] && place.address_components[0].short_name || ''),
                    (place.address_components[1] && place.address_components[1].short_name || ''),
                    (place.address_components[2] && place.address_components[2].short_name || '')
                    ].join(' ');
                }
            console.log(address);
        });
    }
    addAutocomplete(inputFrom, "fromPlace");
    addAutocomplete(inputTo, "toPlace");
}

function fetchWeather(){
    fetch("http://127.0.0.1:8000/api/current_weather")   // First make a GET request to our endpoint
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

// Function that puts bus stations into dropdown menu
// function fetchBusStations() {
//     $.get("https://dublinbus.icu/api/bus_stations", function(data, status) {
//         data["results"].forEach(function(busStation){
//             $(".busStations").append(`<li><p class="busStation">${busStation["fullname"]}</p></li>`);
//         });
//         $("#busStops").on("click", this.currentTarget, updateDropDown);
//     });
// }

function updateDropDown(element){
    // Reference: https://stackoverflow.com/questions/8482241/selecting-next-input
        $("#Bus").val(element.target.innerText);  
}

function searchForRoute(){         // Function for the search button (what happens after the user clicks on "Search")
    console.log("searching");
    calculateAndDisplayRoute(directionsService, directionsDisplay);
    var object = new Object();
    object.From = { 
        Name: $("#fromStation").val(), 
        Lat: fromPlace.lat,
        Lng: fromPlace.lng
    }
    object.To = {
        Name: $("#toStation").val(),
        Lat: toPlace.lat,
        Lng: toPlace.lng
    }
    object.Date  = $("#datepicker input").val();
    object.Time = $("#timePicker").val();
    object.Bus = $("#Bus").val(); 
    const jsonString= JSON.stringify(object);
    console.log(jsonString);
    // console.log(obj1 [, obj2, ..., objN]);
    // getNearestBusStop({ lat: object.From.Lat, lng: object.From.Lng});
    // getNearestBusStop({ lat: object.To.Lat, lng: object.To.Lng});
    // Reference: https://api.jquery.com/jquery.post/

    // Send data to api
    // $.post("http://127.0.0.1:8000/api/make_prediction_using_coordinates", jsonString, function(response) {
    //     console.log( "success" );
    //     console.log("response: " + response);
    // })
    // // When response is ready
    // .done(function() {
    //     console.log( "Display prediction to user" );
    // })
    // // api failure
    // .fail(function() {
    //     $("#prediciton").text(`Predicted travel time: ${16} minutes`);
    //     console.log( "error" );
    // })
    // // Always run
    // .always(function() {
    //     console.log( "finished" );
    // });
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



// Function for the nearest bus stops
// Reference: https://stackoverflow.com/questions/9340800/detect-the-nearest-transit-stop-from-the-given-location
// function getNearestBusStop(center){
    
//     var callback = function(results, status) {
//         // console.log(results);
//         if (status == "OK") {
//             // for (var i = 0; i < results.length; i++) {
//             for (var i = 0; i < 5; i++) {
//                 createMarker({ lat: results[i].geometry.location.lat(), lng: results[i].geometry.location.lng()});
//             }
//         }
//     }
//     var request = {
//         location: center,
//         radius: 1200,
//         types: ["bus_station"]
//     };
//     service = new google.maps.places.PlacesService(map);
//     service.search(request, callback);
// }



function createMarker(location) {
    var marker = new google.maps.Marker({
        position: location, 
        map: map,
        draggable: true,
        animation: google.maps.Animation.DROP
    });
}













// function predict(){
//     let data = {
//         // hour:  $("#timePicker").val(),
//         // day: $("#timePicker").val(),
//         hour:  new Date().getHours(),
//         day: new Date().getDay(),
//         temp: tempNow,
//         rain: rainNow,
//         route: $("#Bus").val(),
//         startStop: $("#fromStation").val(),
//         endStop: $("#toStation").val(),
//     };
//     const jsonString= JSON.stringify(data);
//     $.post("https://dublinbus.icu/api/make_prediction", jsonString)
//         .done(function(data) {
//             $("#prediciton").text(`Predicted travel time: ${data["result"]} minutes`);
//         })
//         .fail(function(data) {
//             $("#prediciton").text("Unable to predict travel time");
//         });

//     $.get("https://dublinbus.icu/api/make_prediction", function(predict) {
//         // keyrir þegar búið er að ná í gogn 
//     });
// }







































// Copyed from Peter
// function makePredictionNow(){
//     let data = {
//         hour: hourNow,
//         day: dayNow,
//         temp: tempNow,
//         rain: rainNow,
//         route: document.getElementById("Bus").value,
//         startStop: document.getElementById("fromStation").value,
//         endStop: document.getElementById("toStation").value
//     };

//     fetch("https://dublinbus.icu/api/make_prediction", {
//         method: "POST",
//         headers: {"Content-Type": "application/json; charset=utf-8"},
//         referrer: "no-referrer",
//         body: JSON.stringify(data)
//       })
//           .then(function(response){
//               return response.json(); // Currently only returning a single value. Using JSON to allow easier extension later
//           })
//           .then(function(prediction){
//               document.getElementById("prediction").innerHTML = `Estimated time: <b>${prediction["result"]}</b> minutes`;
//           })
//           .catch(function(){
//               document.getElementById("prediction").innerHTML = "Prediction server not available."
//           });
//   }
  
//   I ignored the getLatestWeather function from Peters test js
// function getLatestWeather(){
//     fetch("https://dublinbus.icu/api/current_weather")
//         .then(function(response){
//             return response.json();
//         })
//         .then(function(weather){
//             tempNow = weather["temp"];
//             rainNow = weather["precip_intensity"];
//         })
//         .then(function(){console.log(tempNow); console.log(rainNow)});
// }

// function routesDropdown(){
//     allBuses.forEach(function(routeNum){
//         let item = document.createElement("option");
//         item.textContent = routeNum;
//         item.value = routeNum;
//         document.getElementById("busStops").appendChild(item);
//     });
// }

// function getStopLocation(stopNumber){
//     fetch("https://dublinbus.icu/api/stop_location", {
//         method: "POST",
//         headers: {"Content-Type": "application/json; charset=utf-8"},
//         referrer: "no-referrer",
//         body: JSON.stringify({stop: stopNumber})
//     })
//     .then(function(response){
//         return response.json();
//     })
//     .then(function(myLatLng){
//         new google.maps.Marker({
//             position: myLatLng,
//             map: map,
//         });
//     });
// }



// Initialize everything. Waits for document to fully load and then start running stuff
// $(document).ready(function(e){
//     setEventListeners();

//     $('.clockpicker').clockpicker({
//         donetext: "",
//         autoclose: true
//     });
//     $( "#datepicker" ).datepicker({
//         autoclose: true,
//         format: "dd/mm/yyyy",
//         startDate: '1d'
//     });
//     setInitialDateTime();
//     // insertBusStations();
//     setInitialClock()
//     // fetchWeather();
//     getLocation();
//     // geoAddress();
// });

$(window).on("load", function(){

    $(".clockpicker").clockpicker({
        donetext: "",
        autoclose: true
    });
    $( "#datepicker" ).datepicker({
        autoclose: true,
        format: "dd/mm/yyyy",
        startDate: '1d'
    });
    setInitialDateTime();
    setInitialClock();
    fetchWeather();
    getLocation($("#findLocationFrom"));
    getLocation($("#findLocationTo"));
    // calculateAndDisplayRoute(directionsService, directionsDisplay);
    autocomplete();
    
    $("#searchButton").on("click", searchForRoute);

});