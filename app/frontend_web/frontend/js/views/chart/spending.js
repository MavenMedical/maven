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
    'models/chartsModels/spendingModel',
    'text!templates/chart/spending.html'
	], function ($, _, Backbone, currentContext, SpendingModel, spendingTemplate) {

    var Spending = Backbone.View.extend({
        el: '.spending',
        template: _.template(spendingTemplate),
        initialize: function () {
            _.bindAll(this, 'render');
	    this.spend = new SpendingModel;
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
					 display:currentContext.get('display')}));

            this.spend.fetch({
                success: function (spend) {

		    var colorArray = ["#0188BB", "#4C2694", "#79B32D", "#FF8500", "#00587A" ]
			//Palette URL: http://colorschemedesigner.com/#3q62mWSE5w0w0
			
                    var category = new Array("Medication", "Labs", "Procedures", "RJS Nursing", "Immunization/Injection");
		    
		    var encs_cost = [];

		    var keys = []
			for (var d in spend.attributes) {
			    keys.push(d);
			}
		    keys.sort();
		    //console.log(spend);
		    //console.log('keys');
		    //console.log(keys);
		    for (var k in keys) {
			var d = keys[k];
			var days_spend = spend.get(d);
			//console.log('outer loop');
			//console.log(days_spend);
			var total=0;
			for (var t in days_spend) {
			    //console.log(days_spend[t]);
			    total += days_spend[t];
			}
			encs_cost.push({
				date: new Date(d),
				    encounter_cost: total
				    });
		    };
		    
		    //console.log('chart');
		    //console.log(encs_cost);
		    
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
		    

                },
                data: $.param(currentContext.toJSON())
            });
            return this;
        }
	});
    return Spending;
});
//Chart codes are in the template file spending.html