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
    'globalmodels/summaryModel', // current patient (if any)
    'widgets/orderList',
    'libs/jquery/jquery-mousestop-event',
], function ($, _, Backbone, contextModel, spendingModel, summaryModel, OrderList) {

    var CostBD = Backbone.View.extend({
        initialize: function (arg) {
            this.template = _.template(arg.template); // this must already be loaded
            this.$el.html(this.template({page: contextModel.get('page')}));
	        summaryModel.on('change', this.update, this);
            spendingModel.on('change', this.update, this);
            this.update();
        },
        events:{
            'click .progress-bar': 'handleClick'
        },
        update: function () {
            var datefilter = null;
            if ('title' in spendingModel.changed) {
                return;
            }
            if ('date' in spendingModel.changed) {
                datefilter = spendingModel.changed['date'];
                //		    $('#costbd-restriction')[0].innerHTML='Only spending on <i><b>'+datefilter.toDateString() +'</b></i> <button id="removedatefilter">(remove filter)</button>';
                $('#costbd-restriction')[0].innerHTML = 'Only spending on <i><b>' + datefilter.toDateString() + '</b></i>';
            } else {
                $('#costbd-restriction')[0].innerHTML = '';
            }

            var colorArray = [];
            var gathered = {};
            var data = [];

            for (var d in spendingModel.attributes) {
                if (Date.parse(d)) {
                    var date = new Date(d);
                    if (!datefilter ||
                        (date.getFullYear() == datefilter.getFullYear() &&
                            date.getMonth() == datefilter.getMonth() &&
                            date.getDate() == datefilter.getDate())) {
                        var days_spend = spendingModel.get(d);
                        for (var t in days_spend) {
                            var base = days_spend[t];
                            if (t in gathered) {
                                base = base + gathered[t];
                            }
                            gathered[t] = base;
                        }
                    }
                }
            }
            for (var k in gathered) {
                data.push({order: k, cost: gathered[k], color:findColor(k)});
                colorArray.push(findColor(k));
            }
            ;
            var fake = function (s) {
                data.push({order: s, cost: 300, color:findColor(s) });
                colorArray.push(findColor(s));
            }
            fake("Imaging");
            fake("Medication");
            fake("Consultation");
            fake("Lab-work");
            fake("Other");

            //clear order-table before filling it
            $('#order-table-1').empty();
            $('#order-table-2').empty();
            $('.progress').empty();

            var flag = true;
            data.forEach(function (entry) {
                //fill order-table
                var image = $('<img>').attr('src', "../images/"+ entry.order.toLowerCase()+"-55x55px.jpg");
                var cost = $('<span class=\"cost-num\">$'+entry.cost+'</span>');
                var lable = $('<span>'+entry.order+'</span>');
                var container = $('<div>').attr('class', 'row');
                var subcontainer = $('<div>').attr('class', 'col-sm-2');

                //image
                $('<div>').attr('class', 'col-sm-3').append(image).appendTo(container);
                //cost
                $(subcontainer).append(
                    $('<div>').attr('class', 'row').append(cost)).appendTo(container);
                //label
                $(subcontainer).append(
                    $('<div>').attr('class', 'row').append(lable)).appendTo(container);

                if(flag){
                    $('#order-table-1').append(container);
                    flag = false;
                } else {
                    $('#order-table-2').append(container);
                    flag = true;
                }

                // fill progress-bar
                var percentage = (entry.cost/summaryModel.get('spending')*100).toFixed(2);

                $('.progress').append(
                    $('<div id="'+entry.order+'" class="progress-bar bgcolor-'+entry.order.toLowerCase()+'">')
                        .attr('style','width: '+percentage+'%').append(percentage+'%'));
            });
        },
        handleClick: function(e){
            var element = $(e.currentTarget);
            console.log(element.attr('id'));

           /* var mousepos;
	    var overlist = false;
	    var orderList = new OrderList({
		template:'<div class="panel-group orderaccordion"> </div>',
		el:$('#mouse-target'),
		typeFilter: 'doesnotexist',
		slice: null,
	    });*/

        }
    });
    return CostBD;
});
//Chart codes are in the template file costbd.html
