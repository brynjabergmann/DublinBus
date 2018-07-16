// Global variable for map
var map;


// Reference from https://developers.google.com/maps/documentation/javascript/adding-a-google-map
function initMap() {                                // Function that initialize and adds the map to the website
    var Dublin = {lat: 53.349805, lng: -6.26031}    // The location of Dublin
    map = new google.maps.Map(                      // The map, centered at Dublin
        document.getElementById('map'), {zoom: 13, center: Dublin});
  }


function fetchWeather(){
    fetch("https://dublinbus.icu/db/current_weather")   // First make a GET request to our endpoint
        .then(function(rawResponse){                    // Once that raw response is received, do something with it,
            return rawResponse.json();                  // in this case, take the string response and convert to a JSON object
        })
        .then(function(weatherJSON){
            // Round the temp to the nearest integer:
            document.getElementById("weatherTemp").innerHTML = Math.round(weatherJSON["temp"]).toString();
            // No Processing for these, just strings:
            // document.getElementById("weatherImage").innerHTML = weatherJSON["icon"];
            document.getElementsByClassName("weatherIcons").setAttribute("id", "fog"["icons"]);
        });
}


// WeatherIcons
// function weatherIcons(){
//     var icons = new Skycons(),
//             list  = [
//                 "clear-day", "clear-night", "partly-cloudy-day",
//                 "partly-cloudy-night", "cloudy", "rain", "sleet", "snow", "wind",
//                 "fog"
//             ],
//             i;
//         for(i = list.length; i--; )
//             icons.set(list[i], list[i]);
//         icons.play();
// }


// Function that puts bus stations into dropdown menu
function fetchBusStations() {
    $.get("https://dublinbus.icu/db/bus_stations", function(data, status) {
        data["results"].forEach(function(busStation){
            $(".busStations").append(`<li><p class="busStation">${busStation["fullname"]}</p></li>`)
        });
        $(".busStation").on("click", this.currentTarget, updateDropDown)
    });
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
        $output
            // .html(location)
            .removeClass('hide');

        var yourLocation = {lat: p.coords.latitude, lng: p.coords.longitude}
        var marker = new google.maps.Marker({position: yourLocation, map: map});
    }

    $button.geolocate({
        onStart: startCB,
        onFinish: finishCB,
        onError: errorCB,
        onSuccess: successCB,
        timeout: 5000
    });
};



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



function searchForRoute(){              // Function that searches the best routes from choosen points
    console.log("searching");
    var object = new Object();
    object.From = $("#fromStation").val();
    object.To = $("#toStation").val();
    object.Date  = $("#datepicker input").val();
    object.Time = $("#timePicker").val();
    const jsonString= JSON.stringify(object);
    console.log(jsonString);
    // Reference: https://api.jquery.com/jquery.post/
    $.post("/db/predictRoute", object, function(response) {
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


function setInitialClock(){
    const time = new Date();
    $("#timePicker").val(`${time.getHours()}:${time.getMinutes()}`);
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



// Initialize everything. Waits for ducoument to fully load and then start running stuff
$(document).ready(function(e){
    setEventListeners();

    $('#timePicker').clockpicker({
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
    // weatherIcons();
});

