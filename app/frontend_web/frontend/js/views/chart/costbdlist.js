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
		if('title' in spend.changed) {
		    return;
		}
		if('date' in spend.changed) {
		    datefilter=spend.changed['date'];
		    $('#costbd-restriction')[0].innerHTML='Only spending on <i><b>'+datefilter.toDateString() +'</b></i>';
 		} else {
		    $('#costbd-restriction')[0].innerHTML='';
		}
		var colorArray = ["#0188BB", "#4C2694", "#79B32D", "#FF8500", "#00587A" ]
		//Palette URL: http://colorschemedesigner.com/#3q62mWSE5w0w0

		var gathered = {};
		var data = [];

		// essentially this code is used in multiple places, let's make a function
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
		output = '<ul>';
		for (var k in gathered) {
		    output +='<li>'+k+': $'+gathered[k]+'</li>';
		};
		output += '</ul>';
		document.getElementById("cost-bd").innerHTML=output;
	    }
	});
    return CostBD;
       });
