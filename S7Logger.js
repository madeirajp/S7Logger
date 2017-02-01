// Hello, this is the javascript for reading the logs and providing them to Highcharts

// where CSV file is stored
var URL = "https://dl.dropboxusercontent.com/u/3685401/S7Logger/workfile.txt"
var dayObjects = []; // array to store days
//var dataArray = []; NOT GLOBAL BUT

// data object
var DayObject = {
    init: function (day, array) {
        this.day = day;
        this.array = [];
    },
    describe: function () {
        var description = this.day;
        return description;
    },
    showArray: function () {
        var items = this.array;
        return items;
    }
};

function getFileFromServer(url, doneCallback) {
    var xhr;
    xhr = new XMLHttpRequest();
    xhr.onreadystatechange = handleStateChange;
    xhr.open("GET", url, true);
    xhr.send();

    // I don't know what this does
    function handleStateChange() {
        if (xhr.readyState === 4) {
            doneCallback(xhr.status == 200 ? xhr.responseText : null);
        } } }
getFileFromServer(URL, function(text) {
    // if file is not found, display error message
    if (text === null) { console.log("404 ") }
    // if file is found, call function
    else { textToObjects(text); }
    } );

// function for modifying the CSV file to objects
function textToObjects(text) {

    // split text into lines by \n (line break)
    var line = text.split('\n');

    // loop every line
    for (var i = 0; i < line.length; i++)  {

        // ignore empty lines if there is any
        if (line[i].length != 1) {

            //split every line by comma
            var linesplit = line[i].split(",");

            // find values
            // example line: "vacuumOn,I,2017-01-23,16:07:01"
            var output = linesplit[0];
            var type = linesplit[1];
            var day = linesplit[2];
            var time = linesplit[3];
            var thisDay = Object.create(DayObject);

            // first day
            if (dayObjects.length == 0) {
                // just create day object
                thisDay.init(day);
                // and push it to array
                dayObjects.push(thisDay);
                // push to array
                thisDay.array.push(output);

                // after the first day, just push unique dates to array
                // checkUnique will push if there are multiple entries on same day
            } else if (checkUnique(day, output)) { // if index i.e. day not found
                // create day object
                thisDay.init(day);
                dayObjects.push(thisDay);
                thisDay.array.push(output);
            }
        }
    }

    // call the visualizing function
    unitTest(); // check the array
    visualize(objectsToArrays());
    //printAllDates();
}

// Unique checking function to days
function checkUnique(daytocheck, output) {
    for (var i=0; i < dayObjects.length; i++) {
        // if day is found in dayObjects, return false
        //console.log(dayObjects[i].thisDay);
        if (dayObjects[i].day == daytocheck) {
            //console.log("Multiple entries found for " + daytocheck);
            //console.log("Data pushed to array: " + output)
            dayObjects[i].array.push(output);
            return false;
        // if not found, return true
        } else {
            //console.log("Unique day found" + daytocheck);
    } }
    return true;
}

// to keep track what we have
function printAllDates() {
    console.log("Dates and their data: ");
    dayObjects.forEach(function (x) {
        console.log(x.describe(), x.showArray());
    });
}

function objectsToArrays() {

    dateArray = [];

    dayObjects.forEach(function (x) {
        dateArray.push(x.describe());
    });

    console.log("DateArray : " + dateArray);

    return dateArray;
}

function unitTest() {
    for (var i = 0; i < dayObjects.length; i++) {
        if (dayObjects[i].array.length == 0) {
            throw "Invalid array item with no data";
        }
    }
}

// visualizing function
function visualize(datearray) {

    // using Highcharts line-basic example here
    Highcharts.chart('container', {
        title: {
            text: 'Maxin kandi',
            x: -20 //center
        },
        subtitle: {
            text: 'https://github.com/mangelma/S7Logger',
            x: -20
        },
        xAxis: {

            // array of days here
            categories: datearray
        },
        yAxis: {

            // only integers
            allowDecimals: false,

            title: {
                text: 'Highs'
            },
            plotLines: [{
                value: 0,
                width: 1,
                color: '#808080'
            }]
        },
        legend: {
            layout: 'vertical',
            align: 'right',
            verticalAlign: 'middle',
            borderWidth: 0
        },

        // output arrays are here:
        series: [{
            name: 'Vacuum',
            data: [1, 3, 2, 8, 4]
        }]
    });
}