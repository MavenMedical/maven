/**
 * Created by Asmaa Aljuhani on 3/11/14.
 */

define([
    // These are path alias that we configured in our main.js
    'jquery',     // lib/jquery/jquery
    'underscore', // lib/underscore/underscore
    'backbone',    // lib/backbone/backbone
    'currentContext',
    //model
    'text!templates/templatesA/chart/spending.html'
], function ($, _, Backbone, currentContext, spendingTemplate) {

    var Spending = Backbone.View.extend({
        el: '.spending',
        template: _.template(spendingTemplate),
        initialize: function () {
            _.bindAll(this, 'render');
            this.render();
        },
        render: function () {
            console.log('spending');
            var that = this;
            patientName = currentContext.get('patientName');
            if (!patientName) {
                patientName = 'All Patients';
            }

            that.$el.html(that.template({patientName: patientName,
                display: currentContext.get('display')}));

        },
        events: {
            'click': 'click'
        },
        click: function () {
            console.log('clicked');
        },
        update: function (spend) {
            titlefilter = null;
            if ('date' in spend.changed) {
                return;
            }
            if ('title' in spend.changed) {
                titlefilter = spend.changed['title'];
            }

            var colorArray = ["#0188BB", "#4C2694", "#79B32D", "#FF8500", "#00587A" ]
            //Palette URL: http://colorschemedesigner.com/#3q62mWSE5w0w0

            var category = {};

            var encs_cost = [];

            var keys = []
            for (var d in spend.attributes) {
                if (Date.parse(d)) {
                    keys.push(d);
                }
            }
            keys.sort();
            for (var k in keys) {
                var d = keys[k];
                var days_spend = spend.get(d);
                var total = 0;
                for (var t in days_spend) {
                    if (!titlefilter || t == titlefilter) {
                        total += days_spend[t];
                    }
                }
                encs_cost.push({
                    date: new Date(d),
                    encounter_cost: total
                });
            }
            ;

            var chart = AmCharts.makeChart("total-spend", {
                "type": "serial",
                "dataDateFormat": "YYYY-MM-DD",
                "colors": colorArray,
                "pathToImages": "js/amcharts/images/",
                "dataProvider": encs_cost,
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
                        "balloonText": "[[category]]<br /><b><span style='font-size:14px;'>$[[value]]</span></b>",
                        //"bullet": "round",
                        //"bulletBorderAlpha": 1,
                        //"bulletColor":"#FFFFFF",
                        //"hideBulletsCount": 30,
                        // "title": "red line",
                        "valueField": 'encounter_cost',
                        //"useLineColorForBulletBorder":true,
                        "fillAlphas": .8,
                        "fillColorsField": "fill",
                        "inside": true,
                        "type": "column"
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
                "categoryField": 'date',
                "categoryAxis": {
                    "parseDates": true,
                    "axisColor": "#DADADA",
                    "dashLength": 1,
                    "minorGridEnabled": true
                }

            });
            // Note that this refers to the object whose change generated the call to update
            // In this case that is a spendingModel object.
            var that = this;
            chart.addListener("clickGraphItem", function (x) {
                that.clickDate(x, that);
            });
        }
    });


    return Spending;
});
//Chart codes are in the template file spending.html