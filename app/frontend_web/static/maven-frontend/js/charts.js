/**
 * Created by devel on 2/25/14.
 */

var colorArray = ["#0188BB", "#4C2694", "#79B32D", "#FF8500", "#00587A" ]
//Palette URL: http://colorschemedesigner.com/#3q62mWSE5w0w0

var pateint = {
    "name": "John Smith",
    "sex": "Male",
    "DOB": "08/05/1987",
    "problemlist": ["Asthma without status asthmaticus", "Unspecified asthma", "Bronchitis, not specified as acute or chronic",
        "Posthemiplegic athetosis", "Nonspecific abnormal auditory function study" ]};

var encounter = {
    "type": "Hospital Encounter",
    "Contact Date": "12/15",
    "Admitted": "12/15",
    "Discharge": "12/19",
    "orderables": [
        {
            "order": "ECG",
            "cost": "1200"
        },
        {
            "order": "CBC",
            "cost": "38"
        },
        {
            "order": "CRP",
            "cost": "47"
        }
    ]
};


var category = new Array("Medication", "Labs", "Procedures", "RJS Nursing", "Immunization/Injection");

// dashboard charts
var dr_cost_bd = [];
var dr_total_spending = [];

// Alert charts and data
var alerts_num = [];
var alert_action = [
    {
        action: "Followed",
        vol: Math.floor((Math.random() * 100) + 1)
    },
    {
        action: "Ignored",
        vol: Math.floor((Math.random() * 100) + 1)
    }
];
var pot_saving = Math.floor((Math.random() * 100000) + 1);

// Patient charts and data
var utilization = Math.floor((Math.random() * 100000) + 1);
var pat_saving = Math.floor((Math.random() * 100000) + 1);
var pat_cost_bd = [];
var encs_cost = [];

// encounter
var enc_cost_per_day = [
    {
        "date": "2013-12-15",
        "cost": 380
    },
    {
        "date": "2013-12-16",
        "cost": 470
    },
    {
        "date": "2013-12-17",
        "cost": 300
    },
    {
        "date": "2013-12-18",
        "cost": 1200
    },
    {
        "date": "2013-12-19",
        "cost": 470
    }
];

var enc_cost_bd = encounter["orderables"];


generateChartData();


function generateChartData() {

    var firstDate = new Date();
    firstDate.setDate(firstDate.getDate() - 30);
    firstDate.setHours(0, 0, 0, 0);

    for (var i = 0; i < 30; i++) {
        var newDate = new Date(firstDate);
        newDate.setDate(newDate.getDate() + i);


        var sum = 0;

        //loop to generate data for soat breakdown
        var randcost = 0;
        for (var j = 0; j < category.length; j++) {
            randcost = Math.round(Math.random() * 1000);
            dr_cost_bd.push({
                date: newDate,
                cat: category[j],
                cost: randcost
            });

            sum = sum + randcost;
        }


        dr_total_spending.push({
            date: newDate,
            spend: sum,
            subdata: dr_cost_bd
        })
        dr_cost_bd = [];

        //Alert
        alerts_num.push({
            date: newDate,
            alerts: Math.floor((Math.random() * 10) + 1)
        });


        //Encounters for patients
        var count = 0;

        //loop to generate data for soat breakdown
        var rcost = 0;
        for (var j = 0; j < Math.floor((Math.random() * category.length) + 1); j++) {
            rcost = Math.round(Math.random() * 1000)
            pat_cost_bd.push({
                date: newDate,
                cat: category[j],
                cost: rcost
            });

            count = count + rcost;
        }

        encs_cost.push({
            date: newDate,
            encounter_cost: count,
            subdata: pat_cost_bd

        });

        pat_cost_bd = [];
    }


}
function showdashboard() {
    console.log("Dashboard Chart");
    //dashboard charts
    draw_serial_chart("column", "total-spend", dr_total_spending, "date", "spend", "cost-bd", "cat", "cost");
}

function showpatient() {
    console.log("Patient Chart");
    //Patient charts
    draw_serial_chart("step", "encounters_chart", encs_cost, "date", "encounter_cost", "pat-cost-bd", "cat", "cost");

}

function showencounter() {
    draw_orders_bd_chart();
    draw_daily_cost_chart()
}

function showalert() {
    alerts_chart();
alerts_action();
}
AmCharts.ready(function () {

});


function draw_pie_chart(div, data, title, value) {
    AmCharts.makeChart(div, {
        "type": "pie",
        "colors": colorArray,
        "dataProvider": data,
        "titleField": title,
        "valueField": value,
        "labelRadius": 5,

        "radius": "22%",
        "innerRadius": "50%",
        "labelText": "[[title]]"
    });
}

// THis function takes parameters for 2 charts
// Main chart : div (div tag to hold the chart), data (json object that has subdata for the second chart),
//              cat (cateogry) , value (value)
// Sub Chart  : subdiv , subcat (sub category) , subval (sub value)
function draw_serial_chart(chart_type, div, data, cat, value, subdiv, subcat, subval) {
    console.log(data);
    var chart = AmCharts.makeChart(div, {
        "type": "serial",
        "colors": colorArray,
        "pathToImages": "js/amcharts/images/",
        "dataProvider": data,
        "valueAxes": [
            {
                "axisAlpha": 1,
                "dashLength": 1,
                "position": "left"
            }
        ],
        "graphs": [
            {
                "id": "g1",
             "balloonText": "[[category]]<br /><b><span style='font-size:14px;'>$[[value]]</span></b></br> Click to see the cost breakdown",
                "bullet": "round",
                //"bulletBorderAlpha": 1,
                //"bulletColor":"#FFFFFF",
                "hideBulletsCount": 30,
                // "title": "red line",
                "valueField": value,
                //"useLineColorForBulletBorder":true,
                "fillAlphas": .8,
                "fillColorsField": "fill",
                "inside": true,
                "type": chart_type
            }
        ],
        "chartScrollbar": {
            "autoGridCount": true,
            "graph": "g1",
            "scrollbarHeight": 40
        },

        "chartCursor": {
            "cursorPosition": "mouse",
            "cursorColor": colorArray[3]
        },
        "categoryField": cat,
        "categoryAxis": {
            "parseDates": true,
            "axisColor": "#DADADA",
            "dashLength": 1,
            "minorGridEnabled": true
        }

    });

    chart.addListener("rendered", function (event) {
        chart.zoomToIndexes(data.length - 40, data.length - 1);
    });

    chart.addListener("clickGraphItem", function (event) {
        // let's look if the clicked graph item had any subdata to drill-down into
        if (event.item.dataContext.subdata != undefined) {
            // wow it has!
            // let's set that as chart's dataProvider
            // event.chart.dataProvider = event.item.dataContext.subdata;
            if (chart_type == "column") // changing colors with step doesn't show the right thing
            {
                event.item.dataContext.fill = colorArray[2];
                console.log(event.item.bulletGraphics);//.bullet.bulletColor = colorArray[1];
                event.chart.validateData();
                event.item.dataContext.fill = colorArray[0];
            }

            draw_pie_chart(subdiv, event.item.dataContext.subdata, subcat, subval);

            document.getElementById("date").innerHTML = " for " + event.item.dataContext.date.toDateString();

        }
    });

}

// Encounter Charts

function draw_orders_bd_chart() {

    var chart = AmCharts.makeChart("orders_bd", {
        "type": "pie",
        "colors": colorArray,
        "dataProvider": encounter.orderables,
        "titleField": "order",
        "valueField": "cost",
        "labelRadius": 5
    });


}


function draw_daily_cost_chart() {

    var chart = AmCharts.makeChart("daily_cost", {
        "type": "serial",
        "colors": colorArray,
        "dataDateFormat": "YYYY-MM-DD",
        "dataProvider": [
            {
                "date": "2013-12-15",
                "cost": 380
            },
            {
                "date": "2013-12-16",
                "cost": 470
            },
            {
                "date": "2013-12-17",
                "cost": 300
            },
            {
                "date": "2013-12-18",
                "cost": 1200
            },
            {
                "date": "2013-12-19",
                "cost": 470
            }
        ],
        "categoryField": "date",
        "rotate": true,

        "categoryAxis": {
            "gridPosition": "start",
            "axisColor": "#DADADA"
        },
        "valueAxes": [
            {
                "axisAlpha": 0.2
            }
        ],
        "graphs": [
            {
                "type": "column",
                "valueField": "cost",
                "lineAlpha": 0,
                "fillColors": colorArray[0],
                "fillAlphas": 0.8,
                "balloonText": "Expenses in [[category]]:<b>$[[value]]</b>"
            }
        ]
    });
}


//Alerts Chart
function alerts_chart() {
    console.log(alerts_num);
    alerts_num.push({date: "2013-02-28",
        alerts: 5,
        bullet: "round"});

    var chart = new AmCharts.makeChart("num_of_alerts", {
        "type": "serial",
        "theme":"none",
        "dataProvider": alerts_num,
        "categoryField":"date",
        "autoMargins":false,
        "marginLeft":0,
        "marginRight": 5,
        "marginTop":0,
        "marginBottom":0,

        "graphs" :[
            {
                "valueField": "alerts",
                "bulletField" : "bullet",
                "showBalloon":false,
                "lineColor": colorArray[0],
                "fillAlphas": 0.8
            }],
        "valueAxes": [{
            "gridAlpha":0,
            "axisAlpha":0,
            "startOnAxis":true
        }]


    });
}


function alerts_action(){
     // percent chart
    var chart = new AmCharts.AmSerialChart(AmCharts.themes.none);
    chart.dataProvider = [{
        x: 1,
        y1: 80,
        y2: 20
    }];
    chart.categoryField = "x";
    chart.rotate = true;
    chart.autoMargins = false;
    chart.marginLeft = 0;
    chart.marginRight = 0;
    chart.marginTop = 0;
    chart.marginBottom = 0;

    var graph = new AmCharts.AmGraph();
    graph.valueField = "y1";
    graph.type = "column";
    graph.fillAlphas = 0.8;
    graph.fillColors = colorArray[2];
    graph.gradientOrientation = "horizontal";
    graph.lineColor = "#FFFFFF";
    graph.labelText = "[[y1]]% Followed";

    chart.addGraph(graph);

    var graph2 = new AmCharts.AmGraph();
    graph2.valueField = "y2";
    graph2.type = "column";
    graph2.fillAlphas = 0.8;
    graph2.fillColors = colorArray[0];
    graph2.lineColor = "#FFFFFF";
    graph2.labelText = "[[y2]]% Ignored";


    chart.addGraph(graph2);

    var valueAxis = new AmCharts.ValueAxis();
    valueAxis.gridAlpha = 0;
    valueAxis.axisAlpha = 0;
    valueAxis.stackType = "100%"; // this is set to achieve that column would occupie 100% of the chart area
    chart.addValueAxis(valueAxis);

    var categoryAxis = chart.categoryAxis;
    categoryAxis.gridAlpha = 0;
    categoryAxis.axisAlpha = 0;


    chart.write("percent1");


}


