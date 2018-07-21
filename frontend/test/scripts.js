function makePredictionNow(){
    let data = {
        hour: hourNow,
        day: dayNow,
        temp: tempNow,
        rain: rainNow,
        route: document.getElementById("routesDropdown").value,
        startStop: document.getElementById("firstStop").value,
        endStop: document.getElementById("lastStop").value
    };

    fetch("https://dublinbus.icu/api/make_prediction", {
      method: "POST",
      headers: {"Content-Type": "application/json; charset=utf-8"},
      referrer: "no-referrer",
      body: JSON.stringify(data)
    })
        .then(function(response){
            return response.json(); // Currently only returning a single value. Using JSON to allow easier extension later
        })
        .then(function(prediction){
            document.getElementById("prediction").innerHTML = `Estimated time: <b>${prediction["result"]}</b> minutes`;
        })
        .catch(function(){
            document.getElementById("prediction").innerHTML = "Prediction server not available."
        });
}

function getLatestWeather(){
    fetch("https://dublinbus.icu/api/current_weather")
        .then(function(response){
            return response.json();
        })
        .then(function(weather){
            tempNow = weather["temp"];
            rainNow = weather["precip_intensity"];
        })
        .then(function(){console.log(tempNow); console.log(rainNow)});
}

function routesDropdown(){
    allBuses.forEach(function(routeNum){
        let item = document.createElement("option");
        item.textContent = routeNum;
        item.value = routeNum;
        document.getElementById("routesDropdown").appendChild(item);
    });
}

function getStopLocation(stopNumber){
    fetch("https://dublinbus.icu/api/stop_location", {
        method: "POST",
        headers: {"Content-Type": "application/json; charset=utf-8"},
        referrer: "no-referrer",
        body: JSON.stringify({stop: stopNumber})
    })
    .then(function(response){
        return response.json();
    })
    .then(function(myLatLng){
        new google.maps.Marker({
            position: myLatLng,
            map: map,
        });
    });
}


// Taken directly from Brynja's map code:

// Global variable for map
var map;


// Reference from https://developers.google.com/maps/documentation/javascript/adding-a-google-map
function initMap() {                                // Function that initialize and adds the map to the website
    var Dublin = {lat: 53.349805, lng: -6.290310}    // The location of Dublin
    map = new google.maps.Map(                      // The map, centered at Dublin
        document.getElementById('map'), {zoom: 12, center: Dublin});
}





/* * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * *
*                                                                        *
* GLOBAL VARIABLES. THERE ARE BETTER WAYS TO DO THIS. THIS IS TEMPORARY  *
*                                                                        *
* * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * */

const today = new Date();
const hourNow = today.getHours();
const dayNow = today.getDay();
let tempNow;
let rainNow;

const allBuses = [
    "1",
    "102",
    "104",
    "11",
    "111",
    "114",
    "116",
    "118",
    "120",
    "122",
    "123",
    "13",
    "130",
    "14",
    "140",
    "142",
    "145",
    "14C",
    "15",
    "150",
    "151",
    "15A",
    "15B",
    "16",
    "161",
    "16C",
    "17",
    "17A",
    "18",
    "184",
    "185",
    "220",
    "236",
    "238",
    "239",
    "25",
    "25A",
    "25B",
    "25D",
    "25X",
    "26",
    "27",
    "270",
    "27A",
    "27B",
    "27X",
    "29A",
    "31",
    "31A",
    "31B",
    "31D",
    "32",
    "32X",
    "33",
    "33A",
    "33B",
    "33X",
    "37",
    "38",
    "38A",
    "38B",
    "38D",
    "39",
    "39A",
    "4",
    "40",
    "40B",
    "40D",
    "41",
    "41A",
    "41B",
    "41C",
    "41X",
    "42",
    "42D",
    "43",
    "44",
    "44B",
    "45A",
    "46A",
    "46E",
    "47",
    "49",
    "51D",
    "51X",
    "53",
    "54A",
    "56A",
    "59",
    "61",
    "63",
    "65",
    "65B",
    "66",
    "66A",
    "66B",
    "66X",
    "67",
    "67X",
    "68",
    "68A",
    "68X",
    "69",
    "69X",
    "7",
    "70",
    "70D",
    "75",
    "757",
    "76",
    "76A",
    "77A",
    "77X",
    "79",
    "79A",
    "7A",
    "7B",
    "7D",
    "83",
    "83A",
    "84",
    "84A",
    "84X",
    "9"
];

// Do these things as soon as page loads:
document.addEventListener('DOMContentLoaded', function() {
    routesDropdown();
    getLatestWeather();
});
