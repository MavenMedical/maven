/**
 * Created by devel on 2/26/14.
 */
/**
 * Created by devel on 2/25/14.
 */

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
            "cost": "$1200"
        },
        {
            "order": "CBC",
            "cost": "$38"
        },
        {
            "order": "CRP",
            "cost": "$47"
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
        "Date": "12/15",
        "Cost": 380
    },
    {
        "Date": "12/16",
        "Cost": 470
    },
    {
        "Date": "12/17",
        "Cost": 300
    },
    {
        "Date": "12/18",
        "Cost": 1200
    },
    {
        "Date": "12/19",
        "Cost": 470
    }
];

var enc_cost_bd = encounter["orderables"];

generateChartData();

function generateChartData() {

    var firstDate = new Date();
    firstDate.setDate(firstDate.getDate() - 500);
    firstDate.setHours(0, 0, 0, 0);

    for (var i = 0; i < 360; i++) {
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


        //Alert
        alerts_num.push({
            date: newDate,
            alerts: Math.floor((Math.random() * 100) + 1)
        });


        //Encounters for patients
        var count = 0;

        //loop to generate data for soat breakdown
        var rcost = 0;
        for (var j = 0; j < Math.floor((Math.random() * category.length) + 1); j++) {
            rcost = Math.round(Math.random() * 1000)
            pat_cost_bd.push({
                date: newDate,
                cat: category[Math.floor(Math.random() * category.length)],
                cost: rcost
            });

            count = count + rcost;
        }

        encs_cost.push({
            date: newDate,
            encounter_cost: count
        });
    }

    dr_cost_bd = [];

}

AmCharts.ready(function () {

    //dashboard charts
    draw_serial_chart("total-spend", dr_total_spending, "date", "spend");


});

function draw_pie_chart(div, data, title, value) {
    AmCharts.makeChart(div, {
        "type": "pie",
        "theme": "light",
        "dataProvider": data,
        "titleField": title,
        "valueField": value,
        "labelRadius": 5,

        "radius": "22%",
        "innerRadius": "50%",
        "labelText": "[[title]]"
    });
}


function draw_serial_chart(div,data,cat,value){
    //theme
    AmCharts.theme = AmCharts.themes.light;

    // SERIAL CHART
    chart = new AmCharts.AmSerialChart();
    chart.dataProvider = data;
    chart.categoryField = cat;
    chart.startDuration = 1;

    // AXES
    // category
    var categoryAxis = chart.categoryAxis;
    categoryAxis.dashLength = 5 ;

    // value
    var valueAxis = chart.valueAxes;
    valueAxis.dashLength = 5;

    // GRAPH
    var graph = new AmCharts.AmGraph();
    graph.valueField = value;
    graph.balloonText = "$[[value]]";
    graph.type = "column";
    graph.lineAlpha = 0;
    graph.fillAlphas = 0.8;
    chart.addGraph(graph);


    //Cursor Settings
    var chartCursorSettings = new AmCharts.ChartCursorSettings();
    chartCursorSettings.valueBalloonsEnabled = true;
    chart.chartCursorSettings = chartCursorSettings;

    // Period Selector
    var periodSelector = new AmCharts.PeriodSelector();
    periodSelector.periods = [
        {period: "DD", count: 1, label: "1 day"},
        {period: "DD",  count: 5, label: "5 days"},
        {period: "MM", count: 1,selected: true, label: "1 month"},
        {period: "YYYY", count: 1, label: "1 year"},
        {period: "YTD", label: "YTD"},
        {period: "MAX",  label: "MAX"}
    ];
    chart.periodSelector = periodSelector;

    chart.addListener("clickGraphItem", function (event) {
        // let's look if the clicked graph item had any subdata to drill-down into
        if (event.item.dataContext.subdata != undefined) {
            // wow it has!
            // let's set that as chart's dataProvider
            //event.chart.dataProvider = event.item.dataContext.subdata;
            //event.chart.validateData();
        }
    });
    chart.addListener("rendered", zoomChart);
    zoomChart(data);

    chart.write(div);
}


// this method is called when chart is first inited as we listen for "dataUpdated" event
function zoomChart(data) {
    // different zoom methods can be used - zoomToIndexes, zoomToDates, zoomToCategoryValues
    chart.zoomToIndexes(data.length - 40, data.length - 1);
}


function draw_serial_chart6(div, data, cat, value) {
    //theme
    AmCharts.theme = AmCharts.themes.light;

    var chart = AmCharts.makeChart(div, {
    "type": "serial",
    "theme": "light",
    "pathToImages": "js/amcharts/images/",
    "dataProvider": data,
    "valueAxes": [{
        "axisAlpha": 0.2,
        "dashLength": 1,
        "position": "left"
    }],
    "graphs": [{
        "id":"g1",
        "balloonText": "[[category]]<br /><b><span style='font-size:14px;'>$[[value]]</span></b>",
        "bullet": "round",
        "bulletBorderAlpha": 1,
		"bulletColor":"#FFFFFF",
        "hideBulletsCount": 50,
        "title": "red line",
        "valueField": value,
		"useLineColorForBulletBorder":true,
        "type":"column"
    }],
    "chartScrollbar": {
        "autoGridCount": true,
        "graph": "g1",
        "scrollbarHeight": 40
    },
        periodSelector: {
            periods: [
                {
                    period: "DD",
                    count: 1,
                    label: "1 day"
                },
                {
                    period: "DD",
                    count: 5,
                    label: "5 days"
                },
                {
                    period: "MM",
                    count: 1,
                    label: "1 month"
                },
                {
                    period: "YYYY",
                    count: 1,
                    label: "1 year"
                },
                {
                    period: "YTD",
                    label: "YTD"
                },
                {
                    period: "MAX",
                    selected: true,
                    label: "MAX"
                }
            ]
        },
    "chartCursor": {
        "cursorPosition": "mouse"
    },
    "categoryField": cat,
    "categoryAxis": {
        "parseDates": true,
        "axisColor": "#DADADA",
        "dashLength": 1,
        "minorGridEnabled": true
    },
	"exportConfig":{
	  menuRight: '20px',
      menuBottom: '30px',
      menuItems: [{
      icon: 'http://www.amcharts.com/lib/3/images/export.png',
      format: 'png'
      }]
	}
});

chart.addListener("rendered", zoomChart);
zoomChart(data);
}

// this method is called when chart is first inited as we listen for "dataUpdated" event
function zoomChart(data) {
    // different zoom methods can be used - zoomToIndexes, zoomToDates, zoomToCategoryValues
    chart.zoomToIndexes(data.length - 40, data.length - 1);
}



function draw_stock_chart2(div, data, cat, value) {
    AmCharts.makeChart(div, {
        type: "stock",
        "theme": "light",
        pathToImages: "amcharts/images/",
        dataDateFormat: "YYYY-MM-DD",
        dataSets: [
            {
                dataProvider: data,
                fieldMappings: [
                    {
                        fromField: value,
                        toField: "value"
                    }
                ],
                categoryField: cat
            }
        ],

        panels: [
            {

                legend: {},

                stockGraphs: [
                    {
                        id: "graph1",
                        valueField: "value",
                        type: "step",
                        fillAlphas: 1
                    }
                ]
            }
        ],

        panelsSettings: {
            startDuration: 1
        },

        categoryAxesSettings: {
            dashLength: 5
        },

        valueAxesSettings: {
            dashLength: 5
        },

        chartScrollbarSettings: {
            graph: "graph1",
            graphType: "line"
        },

        chartCursorSettings: {
            valueBalloonsEnabled: true
        },

        periodSelector: {
            periods: [
                {
                    period: "DD",
                    count: 1,
                    label: "1 day"
                },
                {
                    period: "DD",
                    count: 5,
                    label: "5 days"
                },
                {
                    period: "MM",
                    count: 1,
                    label: "1 month"
                },
                {
                    period: "YYYY",
                    count: 1,
                    label: "1 year"
                },
                {
                    period: "YTD",
                    label: "YTD"
                },
                {
                    period: "MAX",
                    selected: true,
                    label: "MAX"
                }
            ]
        }
    });

    // event listener
    AmCharts.addListener("clickGraphItem", function (event) {
        alert("clicked");
    });



    /*
    function draw_stock_chart(div, data, cat, value) {
    //theme
    AmCharts.theme = AmCharts.themes.light;

    //serial chart
    var chart = new AmCharts.AmSerialChart();
    chart.pathToImages = "js/amcharts/images/";

    //chart data
    var dataSet = new AmCharts.DataSet();
    dataSet.dataProvider = data;
    dataSet.fieldMappings = [
        {fromField: value, toField: "value"}
    ];
    dataSet.categoryField = cat;
    chart.dataSets = [dataSet];
    chart.dataDateFormat = "YYYY-DD-MM";

    //stock panel
    var stockPanel = new AmCharts.StockPanel();
    chart.panels = [stockPanel];
    var panelsSettings = new AmCharts.PanelsSettings();
    panelsSettings.startDuration = 1;
    chart.panelsSettings = panelsSettings;

    //Graph
    var graph = new AmCharts.StockGraph();
    graph.valueField = "value";
    graph.type = "column"; //step
    graph.fillAlphas = 1;
    graph.title = "Value";
    graph.balloonText = "$[[value]]";
    stockPanel.addStockGraph(graph);

    //categoryAxes Settings
    var categoryAxesSettings = new AmCharts.CategoryAxesSettings();
    categoryAxesSettings.dashLength = 5;
    chart.categoryAxesSettings = categoryAxesSettings;

    // value Axes Settings
    var valueAxesSettings = new AmCharts.ValueAxesSettings();
    valueAxesSettings.dashLength = 5;
    chart.valueAxesSettings = valueAxesSettings;

    // Scrollbar Settings
    var chartScrollbarSettings = new AmCharts.ChartScrollbarSettings();
    chartScrollbarSettings.graph = graph;
    chartScrollbarSettings.graphType = "line";
    chart.chartScrollbarSettings = chartScrollbarSettings;

    //Cursor Settings
    var chartCursorSettings = new AmCharts.ChartCursorSettings();
    chartCursorSettings.valueBalloonsEnabled = true;
    chart.chartCursorSettings = chartCursorSettings;

    // Period Selector
    var periodSelector = new AmCharts.PeriodSelector();
    periodSelector.periods = [
        {period: "DD", count: 1, label: "1 day"},
        {period: "DD",  count: 5, label: "5 days"},
        {period: "MM", count: 1,selected: true, label: "1 month"},
        {period: "YYYY", count: 1, label: "1 year"},
        {period: "YTD", label: "YTD"},
        {period: "MAX",  label: "MAX"}
    ];
    chart.periodSelector = periodSelector;



    //draw chart
    chart.write(div);


}
     */
}