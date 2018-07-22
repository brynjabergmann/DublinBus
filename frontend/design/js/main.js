// Global variable for map
var map;


// Reference from https://developers.google.com/maps/documentation/javascript/adding-a-google-map
function initMap() {                                // Function that initialize and adds the map to the website
    var Dublin = {lat: 53.349805, lng: -6.290310}    // The location of Dublin
    map = new google.maps.Map(                      // The map, centered at Dublin
        document.getElementById('map'), {zoom: 12, center: Dublin});
  }

  
  
  function getLocation(){             // Function to get the users geo location
    //Reference: https://github.com/rodaine/jQuery-Geolocation/blob/master/demo.html
    var $button = $('#locate');     
    var $output = $('#output');     
    var startCB = function() {      
        $output.addClass('hide');
        $button
            .addClass('working')
            .attr('disabled', 'disabled'); 
    }
    var finishCB = function() { 
        $button
            .removeClass('working')
            .removeAttr('disabled'); 
    }
    var errorCB = function(error) { 
        alert( 'Error ' + error.code + ':' + error.message ); 
    }
    var successCB = function(p) {
        var location = 'Latitude: ' + p.coords.latitude + '<br/>' 
            + 'Longitude: ' + p.coords.longitude;
        var yourLocation = {lat: p.coords.latitude, lng: p.coords.longitude}
        var marker = new google.maps.Marker({
            position: yourLocation, 
            map: map,
            draggable: true,
            animation: google.maps.Animation.DROP
        });
        marker.addListener('click', toggleBounce);
        $output
            // .html(location)
            .removeClass('hide');
            geoAddress(yourLocation);

        // Reference: https://developers.google.com/maps/documentation/javascript/examples/marker-animations
        function toggleBounce() {
            if (marker.getAnimation() !== null) {
              marker.setAnimation(null);
            } else {
              marker.setAnimation(google.maps.Animation.BOUNCE);
            }
          }
    }

    $button.geolocate({
        onStart: startCB,
        onFinish: finishCB,
        onError: errorCB,
        onSuccess: successCB,
        timeout: 5000
    });
};

function geoAddress(location){
    var geocoder = new google.maps.Geocoder();
    // Reference: https://developers.google.com/maps/documentation/javascript/examples/geocoding-reverse
    geocoder.geocode({'location': location}, function(results, status){
        if (status == 'OK') {
            if (results[0]) {
                // var streetNumber = results[0]["address_components"].find(function(element){
                //     return element.types.includes("street_number");})["long_name"];
                var route = results[0]["address_components"].find(function(element){
                    return element.types.includes("route");})["long_name"];
                var postalcode = results[0]["address_components"].find(function(element){
                    return element.types.includes("postal_town");})["long_name"];
                var country = results[0]["address_components"].find(function(element){
                        return element.types.includes("country", "political");})["long_name"];
                $("#fromStation").val(`${route}, ${postalcode}, ${country}`);
                }
        }
        console.log(results[0]);
    });

}

// Reference: https://developers.google.com/maps/documentation/javascript/places-autocomplete
function autocomplete(){
    // var input = $('#fromStation');
    var inputFrom = document.getElementById('fromStation');
    var inputTo = document.getElementById('toStation');

    function addAutocomplete(input) {
        console.log(input);
        var autocomplete = new google.maps.places.Autocomplete(input);
        // Bind the map's bounds (viewport) property to the autocomplete object,
            // so that the autocomplete requests use the current map bounds for the
            // bounds option in the request.
            autocomplete.bindTo('bounds', map);
            // Set the data fields to return when the user selects a place.
            autocomplete.setFields(
                ['address_components']);
            autocomplete.addListener('place_changed', function() {
                var place = autocomplete.getPlace();
                
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
    addAutocomplete(inputFrom);
    addAutocomplete(inputTo);
}



function fetchWeather(){
    fetch("https://dublinbus.icu/api/current_weather")   // First make a GET request to our endpoint
        .then(function(rawResponse){                    // Once that raw response is received, do something with it,
            return rawResponse.json();                  // in this case, take the string response and convert to a JSON object
        })
        .then(function(weatherJSON){
            // Round the temp to the nearest integer
            document.getElementById("weatherTemp").innerHTML = Math.round(weatherJSON["temp"]).toString();
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
function fetchBusStations() {
    $.get("https://dublinbus.icu/api/bus_stations", function(data, status) {
        data["results"].forEach(function(busStation){
            $(".busStations").append(`<li><p class="busStation">${busStation["fullname"]}</p></li>`)
        });
        $(".busStation").on("click", this.currentTarget, updateDropDown)
    });
}






function updateDropDown(element){
    // Reference: https://stackoverflow.com/questions/8482241/selecting-next-input
    if(element.target.parentNode.parentNode.id == "fromStations")
    {
        $("#fromStation").val(element.target.innerText);
    }
    else{
        $("#toStation").val(element.target.innerText);
    }
    
}



function searchForRoute(){         // Function that searches the best routes from choosen points
    console.log("searching");
    var object = new Object();
    object.From = $("#fromStation").val();
    object.To = $("#toStation").val();
    object.Date  = $("#datepicker input").val();
    object.Time = $("#timePicker").val();
    const jsonString= JSON.stringify(object);
    console.log(jsonString);
    // Reference: https://api.jquery.com/jquery.post/
    $.post("/api/predictRoute", object, function(response) {
        console.log( "success" );
        console.log("response: " + response);
      })
        .done(function() {
            console.log( "Display prediction to user" );
        })
        .fail(function() {
            console.log( "error" );
        })
        .always(function() {
            console.log( "finished" );
        });
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


// Function for configuring event listeners
function setEventListeners() {
    // $('.search-panel .dropdown-menu').find('p').click(function(e) {
	// 	e.preventDefault();
	// 	var param = $(this).attr("href").replace("#","");
	// 	var concept = $(this).text();
	// 	$('.search-panel span#search_concept').text(concept);
	// 	$('.input-group #search_param').val(param);
    // });
    $('#searchButton').on("click", searchForRoute);

}



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
    setEventListeners();

    $('.clockpicker').clockpicker({
        donetext: "",
        autoclose: true
    });
    $( "#datepicker" ).datepicker({
        autoclose: true,
        format: "dd/mm/yyyy",
        startDate: '1d'
    });
    setInitialDateTime();
    // insertBusStations();
    setInitialClock()
    fetchWeather();
    getLocation();
    autocomplete();
});