// Hello, this is the javascript for reading the logs and providing them to Highcharts

// where CSV file is stored
var URL = "https://dl.dropboxusercontent.com/u/3685401/S7Logger/workfile.txt"
var dayObjects = []; // array to store days

// data object
var DayObject = {
    init: function (day) {
        this.day = day;
    },
    describe: function () {
        var description = this.day;
        return description;
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
    else { textToArray(text); }
    } );

// function for modifying the CSV file to javascript arrays
function textToArray(text) {

    // initializing variables and arrays
    var vacuumCount = 0;
    var datearray = [];
    var vacuumarray = [];
    var armarray = [];
    var magarray = [];

    // split text into lines by \n (line break)
    var line = text.split('\n');

    // loop every line
    for (var i = 0; i < line.length; i++)  {

        //console.log(line[i],line[i].length);

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

            //console.log(i,output, type, day, time);


            // pushing only unique dates to the datearray
            // TODO: make this its own function

            //console.log(day + checkUnique(day));

            // first day
            // we can't know the counts yet so they are not pushed
            if (dayObjects.length == 0) {
                thisDay.init(day);
                dayObjects.push({thisDay: day, data: output});
                //console.log(dayObjects);

                //console.log(thisDay.day);

                // remaining, unique dates and counts
                //
            } else if (checkUnique(day)) { // if index i.e. day not found
                thisDay.init(day);
                //dayObjects.push(thisDay);
                dayObjects.push({thisDay: day, data: output});

                //console.log("new day found in CSV ");

                // push counters to respective arrays
                vacuumarray.push(vacuumCount);
            }



            // counters
            if (output == "vacuumOn") { vacuumCount++; }

        }
        //console.log(dayObjects.indexOf(thisDay.day));
        //console.log(thisDay.day);


    }

    // call the visualizing function
    visualize(datearray, vacuumarray, magarray, armarray);
    console.log(dayObjects);
    //printAllDates();
}

// Unique checking function to days
function checkUnique(daytocheck) {
    for (var i=0; i < dayObjects.length; i++) {
        // if day is found in dayObjects, return false
        if (dayObjects[i].day == daytocheck) {
            console.log("Multiple entries found for " + daytocheck);
            return false;
        // if not found, return true
        } else {
            //console.log("Unique day found" + daytocheck);
    } }
    return true;
}

// to keep track what we have
function printAllDates() {
    console.log("Array: " + dayObjects);
    console.log("Unique dates are: ");
    dayObjects.forEach(function (x) {
        //console.log(x.describe())
        console.log(dayObjects.day);
    });

}

// visualizing function
function visualize(datearray, vacuumarray, magarray, armarray) {

    // using Highcharts line-basic example here
    Highcharts.chart('container', {
        title: {
            text: 'Kumulatiivinen laskuri Distribution Stationin outputeille',
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
            data: vacuumarray
        }, {
            name: 'Mag',
            data: magarray
        }, {
            name: 'Arm',
            data: armarray
        }]
    });
}