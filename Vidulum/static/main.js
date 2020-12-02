$(document).ready(function() {
    console.log("ready!");
    var budget_data = {'test':'test'};


    var pathname = window.location.pathname; // Returns path only (/path/example.html)
    var budget_id = pathname.split("/");
    budget_id = budget_id[budget_id.length-1];

    var origin   = window.location.origin;   // Returns base URL (https://example.com)


    $.get("/api/v1/budget/" + budget_id, function(data, status){
	alert("Data: " + data + "\nStatus: " + status);
	budget_data = data;
    });




    // get basic budget data

    // get budget dashboard










}); //close document ready
