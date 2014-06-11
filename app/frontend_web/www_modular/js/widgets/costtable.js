/**
 * Created by Asmaa Aljuhani on 3/11/14.
 */

define([
    // These are path alias that we configured in our main.js
    'jquery',     // lib/jquery/jquery
    'underscore', // lib/underscore/underscore
    'backbone',    // lib/backbone/backbone
    'globalmodels/contextModel',
    'globalmodels/spendingModel',
], function ($, _, Backbone, contextModel, spendingModel) {

    var CostBD = Backbone.View.extend({
	initialize: function(arg) {
	    this.template = _.template(arg.template); // this must already be loaded
	    this.$el.html(this.template({page: contextModel.get('page')}));
	    spendingModel.on('change', this.update, this);
	    this.update();
	},
	update: function() {
	    var datefilter=null;
	    if('title' in spendingModel.changed) {
		return;
	    }
	    if('date' in spendingModel.changed) {
		datefilter=spendingModel.changed['date'];
		//		    $('#costbd-restriction')[0].innerHTML='Only spending on <i><b>'+datefilter.toDateString() +'</b></i> <button id="removedatefilter">(remove filter)</button>';
		$('#costbd-restriction')[0].innerHTML='Only spending on <i><b>'+datefilter.toDateString() +'</b></i>';
 	    } else {
		$('#costbd-restriction')[0].innerHTML='';
	    }

        /*
         $('#dynamic_enc').append(
                    $('<li>').append(
                        $('<a>').attr('href', '#/episode/'+enc[i][0]+'/patient/'+pat_id).append(
                            $('<i>').attr('class', 'glyphicon glyphicon-time').append(
                                $('<span>').append(' Encounter (' + enc[i][1] + ')')))));


        <div class="row">
            <div class="col-sm-3">
                    <img src="../images/imaging-55x55px.jpg">
                </div>
                <div class="col-sm-2">
                    <div class="row">
                        <span class="cost-num">$180</span>
                    </div>
                    <div class="row">
                        <span>Imaging</span>
                    </div>
                </div>
                </div>
         */
/*
        //fill order-table
        var image = $('<img>').attr('src',"../images/imaging-55x55px.jpg");
        var cost = $('<span>').attr('class','cost-num').value('$170');
        var lable = $('<span>').value('Imaging');

        var container = $('<div>').attr('class','row');

        //image
            $('<div>').attr('class','col-sm-3').append(image).appendTo(container);
        //cost
        $('<div>').attr('class','col-sm-2')
            .append($('<div>').attr('class','row').append(cost)).appendTo(container)
            .append($('<div>').attr('class','row').append(lable)).appendTo(container);







        $('#order-table-1').append(
            $('<div>').attr('class','row').append(
                $('<div>').attr('class','col-sm-3').append(
                    $('<img>').attr('src',"../images/imaging-55x55px.jpg")
                </div>
                <div class="col-sm-2">
                    <div class="row">
                        <span class="cost-num">$180</span>
                    </div>
                    <div class="row">
                        <span>Imaging</span>
                    </div>
                </div>
                </div>'
*/
	    var colorArray = ["#0188BB", "#4C2694", "#79B32D", "#FF8500", "#00587A" ]
	    //Palette URL: http://colorschemedesigner.com/#3q62mWSE5w0w0

	    var gathered = {};
	    var data = [];
	    for (var d in spendingModel.attributes) {
		if(Date.parse(d)) {
		    var date = new Date(d);
		    if(!datefilter ||
		       (date.getFullYear()==datefilter.getFullYear() &&
			date.getMonth()==datefilter.getMonth() &&
			date.getDate()==datefilter.getDate())) {
			var days_spend = spendingModel.get(d);
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
            console.log(k);
            //data.push({k:gathered[k]});
	    };
        console.log(data);
	    var chart = AmCharts.makeChart("cost-bd", {
		"type": "serial",
    "theme": "none",
    "dataProvider": data,
    "colors":colorArray,
    "valueAxes": [{
		"gridAlpha": 0,
		"dashLength": 0
    }],
    "gridAboveGraphs": true,
    "startDuration": 1,
    "graphs": [{
        "balloonText": "[[category]]: <b>$[[value]]</b>",
        "fillAlphas": 0.8,
        "lineAlpha": 0.2,
        "type": "column",
        "valueField": "cost"
    }],
    "chartCursor": {
        "categoryBalloonEnabled": false,
        "cursorAlpha": 0,
        "zoomable": true
    },
    "rotate": true,
    "categoryField": "order",
    "categoryAxis": {
        "gridPosition": "start",
        "gridAlpha": 0
    }
        });
	    chart.addListener("clickGraphItem", spendingModel.clickType, spendingModel);
	    chart.invalidateSize();
//	    $('#cost-db').html('OTHER TEXT');
	}
    });
    return CostBD;
});
//Chart codes are in the template file costbd.html
