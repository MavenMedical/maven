/**
 * Created by Asmaa Aljuhani on 3/11/14.
 */

define([
    // These are path alias that we configured in our main.js
    'jquery',     // lib/jquery/jquery
    'underscore', // lib/underscore/underscore
    'backbone',    // lib/backbone/backbone
    'currentContext',

    'text!templates/chart/costbd.html'
], function ($, _, Backbone, currentContext, costbdTemplate) {

    var CostBD = Backbone.View.extend({
        el: '.costbd',
        template: _.template(costbdTemplate),
        initialize: function(){
		//_.bindAll(this, 'render', 'click');
            this.render();
	    },
        render: function () {
		this.$el.html(this.template({page: currentContext.get('page')}));
		return this;
	    },	
	update: function(spend) {
		var datefilter=null;
		var that=this;
		if('title' in spend.changed) {
		    return;
		}
		if('date' in spend.changed) {
		    datefilter=spend.changed['date'];
		    //		    $('#costbd-restriction')[0].innerHTML='Only spending on <i><b>'+datefilter.toDateString() +'</b></i> <button id="removedatefilter">(remove filter)</button>';
		    $('#costbd-restriction')[0].innerHTML='Only spending on <i><b>'+datefilter.toDateString() +'</b></i>';
 		} else {
		    $('#costbd-restriction')[0].innerHTML='';
		}
		var colorArray = ["#0188BB", "#4C2694", "#79B32D", "#FF8500", "#00587A" ]
		//Palette URL: http://colorschemedesigner.com/#3q62mWSE5w0w0

		var gathered = {};
		var data = [];

		for (var d in spend.attributes) {
		    if(Date.parse(d)) {
			var date = new Date(d);
			if(!datefilter || 
			   (date.getFullYear()==datefilter.getFullYear() && 
			    date.getMonth()==datefilter.getMonth() &&
			    date.getDate()==datefilter.getDate())) {
			    var days_spend = spend.get(d);
			    for (var t in days_spend) {
				var base = days_spend[t];
				if (t in gathered) {
				    base = base + gathered[t];
				}
				gathered[t]=base;
			    }
			}
		    }
		}
		for (var k in gathered) {
		    data.push({order: k,cost: gathered[k]});
		};
		
		var chart = AmCharts.makeChart("cost-bd", {
			"type": "pie",
			"colors": colorArray,
			
			"dataProvider": data,
			"titleField": "order",
			"valueField": "cost",
			"labelRadius": 5,
			"pullOutOnlyOne": true,
			
			"radius": "25%",
			"innerRadius": "60%",
			"labelText": "[[title]]: $[[value]]"
			//"balloonText": "Expenses in [[title]]:<b>$[[value]]</b>"
		    });
		// Note that this refers to the object whose change generated the call to update
		// In this case that is a spendingModel object.
		chart.addListener("pullOutSlice", function(x) {that.clickType(x,that);});
	    }
	});
    return CostBD;
       });

//Chart codes are in the template file costbd.html