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


function fetchWeather(){
    /*
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

// Function for fetching and inserting bus stations to dropdown menus
function insertBusStations(){
    //I think we should create our own api in Django that will only send the bus station names
    //The json file contains too much information and is to slow.
    //We might want to create an api that would enable us to write the first 3 letters of a bus station 
    //and then suggest the names that are similar.  
    $.get("https://data.smartdublin.ie/cgi-bin/rtpi/busstopinformation", (data, status) => { //=> means anonymous function
        data["results"].forEach((busStation) => {
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

// Function that searches the best routes from choosen points
function searchForRoute(){
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
    insertBusStations();
    fetchWeather();
});

