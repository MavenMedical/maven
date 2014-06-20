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
    'widgets/orderList',
    'libs/jquery/jquery-mousestop-event',
], function ($, _, Backbone, contextModel, spendingModel, OrderList) {

    var CostBD = Backbone.View.extend({
	initialize: function(arg) {
	    this.template = _.template(arg.template); // this must already be loaded
	    this.$el.html(this.template({page: contextModel.get('page')}));
	    spendingModel.on('change', this.update, this);
	    this.update();
	},
	update: function() {
	    var datefilter=null;
	    if('typeFilter' in spendingModel.changed) {
		return;
	    }
	    if('dateFilter' in spendingModel.changed) {
		datefilter=spendingModel.changed['dateFilter'];
		//		    $('#costbd-restriction')[0].innerHTML='Only spending on <i><b>'+datefilter.toDateString() +'</b></i> <button id="removedatefilter">(remove filter)</button>';
		$('#costbd-restriction')[0].innerHTML='Only spending on <i><b>'+datefilter.toDateString() +'</b></i>';
 	    } else {
		$('#costbd-restriction')[0].innerHTML='';
	    }

	    var colorArray = [];
	    var data = []
	    var gathered = spendingModel.getGathered();
	    for (var k in gathered) {
		data.push({order: k, cost: gathered[k]});
		colorArray.push(findColor(k));
	    };
	    var fake = function(s) {
		data.push({order:s, cost:300});
		colorArray.push(findColor(s));
	    }
	    fake("Imaging");
	    fake("Medication");
	    fake("Consultation");
	    fake("Lab-work");
	    fake("Other");
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
		"labelText": "[[title]]: $[[value]]",
		"balloonText": "[[title]]<br>$[[value]]<br>[[percents]]%",
	    });

	    chart.addListener("pullOutSlice", function(v) {spendingModel.clickType(v.dataItem.title);}, spendingModel);
	    chart.addListener("pullInSlice", function() {spendingModel.clickType('');}, spendingModel);

	    var curSlice = null;
	    var mousepos;
	    var overlist = false;
	    var orderList = new OrderList({
		template:'<div class="panel-group orderaccordion"> </div>',
		el:$('#mouse-target'),
		typeFilter: 'doesnotexist',
		slice: null,
	    });
	    var maybeHide = function() {
		if(curSlice == null && !overlist) {
		    orderList.slice = null;
		    orderList.$el.hide();
		    orderList.typeFilter = 'does not exist';
		    overlist = false;
		}
	    }
	    chart.addListener("rollOverSlice", function(evt) {curSlice = evt.dataItem;});
	    chart.addListener("rollOutSlice", function() {
		curSlice = null;
		setTimeout(maybeHide,500);
	    });
	    $(orderList.el).mouseover(function() {overlist=true});
	    $(orderList.el).mouseleave(function() {overlist=false; setTimeout(maybeHide,500);});
	    $(this.el).mousemove(function(e) {mousepos=e;});
	    $(this.el).mousestop(1000, function(e) {
		if(curSlice) {
		    orderList.$el[0].style.left = (mousepos.pageX+10)+'px';
		    orderList.$el[0].style.top = (mousepos.pageY-50)+'px';
		    if(curSlice != orderList.slice) {
			orderList.slice = curSlice;
			orderList.typeFilter = curSlice.title;
			orderList.addAll();
		    }
		}
		    
	    });

	    chart.invalidateSize();
	}
    });
    return CostBD;
});
//Chart codes are in the template file costbd.html
