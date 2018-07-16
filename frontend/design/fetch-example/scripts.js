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
        .then(function(weatherJSON){    // Now that we have the JSON object, we can use it however we like:
            // Here I take our "kind of human readable" time string, convert it to UNIX time, and then re-convert it to local time:
            document.getElementById("timestamp").innerHTML = new Date(Date.parse(weatherJSON["timestamp"])).toString();

            // Here we simply want the description string, so there is no processing
            document.getElementById("description").innerHTML = weatherJSON["description"];

            // Here I round the temp to the nearest integer:
            document.getElementById("temperature").innerHTML = Math.round(weatherJSON["temp"]).toString();

            // No Processing for these, just strings:
            document.getElementById("icon").innerHTML = weatherJSON["icon"];
            document.getElementById("precipitation").innerHTML = weatherJSON["precip_intensity"];
        });
}