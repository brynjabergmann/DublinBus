// Initialize and add the map
// Reference from https://developers.google.com/maps/documentation/javascript/adding-a-google-map
function initMap() {
    // The location of Dublin
    var Dublin = {lat: 53.349805, lng: -6.26031}
    // The map, centered at Dublin
    var map = new google.maps.Map(
        document.getElementById('map'), {zoom: 12, center: Dublin});
    // The marker, positioned at Dublin - EF VIÐ VILJUM HAFA MARKER
    // var marker = new google.maps.Marker({position: Dublin, map: map});
  }

// function initSidebar() {
//     console.log("Hallo");
//     $('.search-panel .dropdown-menu').find('a').click(function(e) {
// 		e.preventDefault();
// 		var param = $(this).attr("href").replace("#","");
// 		var concept = $(this).text();
// 		$('.search-panel span#search_concept').text(concept);
// 		$('.input-group #search_param').val(param);
// 	});
//     $('.search-panel1 .dropdown-menu').find('a').click(function(e) {
// 		e.preventDefault();
// 		var param = $(this).attr("href").replace("#","");
// 		var concept = $(this).text();
// 		$('.search-panel1 span#search_concept1').text(concept);
// 		$('.input-group #search_param1').val(param);
// 	});  
// }


// $(document).ready(function(e){
//     initSidebar();
// });

function fetchWeather(){
    /*
    Note that this example won't work if you run it on your local computer, because of a security feature called CORS
    (Cross-Origin Resource Sharing), which means that unless the server *specifically* says that anyone is allowed to
    read the result of a response, only requests made from the same host as the resource
    (i.e. from dublinbus.icu/x to dublinbus.icu/y) are permitted.

    This is on GitLab so you can see the code.
    To see this in action, go to https://dublinbus.icu/fetch-example
    */
    fetch("https://dublinbus.icu/db/current_weather")  // First make a GET request to our endpoint
        .then(function(rawResponse){    // Once that raw response is received, do something with it,
            return rawResponse.json();  // in this case, take the string response and convert to a JSON object
        })
        .then(function(weatherJSON){
            
            // Here I round the temp to the nearest integer:
            document.getElementById("weatherTemp").innerHTML = Math.round(weatherJSON["temp"]).toString();

            // No Processing for these, just strings:
            document.getElementById("weatherImage").innerHTML = weatherJSON["icon"];
        });
}

function insertBusStations(){
    //I think we should create our own api in Django that will only send the bus station names
    //The json file contains too much information.
    //We might want to create an api that would enable us to write the first 3 letters of a bus station 
    //and then suggest the names that are similar.  
    $.get("https://data.smartdublin.ie/cgi-bin/rtpi/busstopinformation", (data, status) => {
        data["results"].forEach((busStation) => {
            $(".busStations").append(`<li>${busStation["fullname"]}</li>`)
        });
    });
}

function searchForRoute(){
    console.log("searching");
    var object = new Object();
    object.From = $("#").val();
    object.To = $("#").val();
    object.Date  = $("#datepicker input").val();
    object.Time = $("#timePicker").val();
    const jsonString= JSON.stringify(object);
}

function setInitialDateTime(){
    const date = new Date();

    $("#datepicker input").val(`${date.getDate()}/${date.getMonth() + 1}/${date.getFullYear()}`);
}

$(document).ready(function(e){
    $('.search-panel .dropdown-menu').find('a').click(function(e) {
		e.preventDefault();
		var param = $(this).attr("href").replace("#","");
		var concept = $(this).text();
		$('.search-panel span#search_concept').text(concept);
		$('.input-group #search_param').val(param);
    });
    $('#searchButton').on("click", searchForRoute);
    
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
    insertBusStations();
    fetchWeather();
});

