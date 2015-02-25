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
    //This is view is to render a table chart for cost breakdown
    //it use spendingModel as its data source
    //It shows each order type and how much it cost,
    // and a bar that shows the percentage of each order type
    // Another equivalent data visiualizing is costdonut
    var CostBD = Backbone.View.extend({
        initialize: function (arg) {
            this.template = _.template(arg.template); // this must already be loaded
            this.$el.html(this.template({page: contextModel.get('page')}));
            summaryModel.on('change', this.update, this);
            spendingModel.on('change', this.update, this);
            this.update();
        },
        events: {
            'click .progress-bar': 'handleClick' // not in use
        },
        update: function () {
            var datefilter = null;
            if ('title' in spendingModel.changed) {
                return;
            }
            if ('date' in spendingModel.changed) {
                datefilter = spendingModel.changed['date'];
                //		    $('#costbd-restriction')[0].innerHTML='Only spending on <i><b>'+datefilter.toDateString() +'</b></i> <button id="removedatefilter">(remove filter)</button>';
                //$('#costbd-restriction')[0].innerHTML = 'Only spending on <i><b>' + datefilter.toDateString() + '</b></i>';
            } else {
                //$('#costbd-restriction')[0].innerHTML = '';
            }

            var colorArray = [];
            var data = [];
            var gathered = spendingModel.getGathered();
            for (var k in gathered) {
                data.push({order: k, cost: gathered[k], color: findColor(k)});
                colorArray.push(findColor(k));
            }

            //The following lines of code is to display the different order types in two columns.
            // there is one element for each column, then based on a flag the appending alternate between these two columns.
            // A better way to do this next time is to have one element and set a bootstrap grid system to 4 (just an example)
            // and set each order to half that number (here is 2)
            //clear order-table before filling it
            $('#order-table-1').empty();
            $('#order-table-2').empty();
            $('.progress').empty();

            var curTitle = null;
            var overlist = false;
            var maybeHide;
            var flag = true;

            // loop for appending data with its icon , cost and label to the table
            data.forEach(function (entry) {
                //fill order-table
                var image = $('<img>').attr('src', "../images/" + entry.order.toLowerCase() + "-55x55px.jpg");
                var cost = $('<span class=\"cost-num\">$' + entry.cost + '</span>');
                var lable = $('<span>' + entry.order + '</span>');
                var container = $('<div>').attr('class', 'row');
                var subcontainer = $('<div>').attr('class', 'col-sm-2');

                // functions to make the view intractable
                container.mouseover(function () {
                    curTitle = entry.order;
                });
                container.mouseleave(function () {
                    curTitle = null;
                    setTimeout(maybeHide, 500);
                });


                //image
                $('<div>').attr('class', 'col-sm-3').append(image).appendTo(container);
                //cost
                $(subcontainer).append(
                    $('<div>').attr('class', 'row').append(cost)).appendTo(container);
                //label
                $(subcontainer).append(
                    $('<div>').attr('class', 'row').append(lable)).appendTo(container);

                // flag to determine which column to add the order element to
                if (flag) {
                    $('#order-table-1').append(container);
                    flag = false;
                } else {
                    $('#order-table-2').append(container);
                    flag = true;
                }

                // fill progress-bar
                var percentage = (entry.cost / summaryModel.get('spending') * 100).toFixed(2);

                $('.progress').append(
                    $('<div id="' + entry.order + '" class="progress-bar bgcolor-' + entry.order.toLowerCase() + '">')
                        .attr('style', 'width: ' + percentage + '%').append(Math.round(percentage) + '%'));
            });


            //when clicking on an order type, a list of the orders from that type will be shown
            // at the same position of the mouse where it was clicked
            var mousepos;
            var orderList = new OrderList({
                template: '<div class="panel-group orderaccordion"> </div>',
                el: $('#mouse-target'),
                typeFilter: 'doesnotexist',
                title: null,
            });
            maybeHide = function () {
                if (curTitle == null && !overlist) {
                    orderList.title = null;
                    orderList.$el.hide();
                    orderList.typeFilter = 'does not exist';
                    overlist = false;
                }
            }
            //chart.addListener("rollOverSlice", function(evt) {curTitle = evt.dataItem;});
            //chart.addListener("rollOutSlice", function() {
//		curTitle = null;
//		setTimeout(maybeHide,500);
//	    });
            $(orderList.el).mouseover(function () {
                overlist = true
            });
            //after certain time the order list will fade out
            $(orderList.el).mouseleave(function () {
                overlist = false;
                setTimeout(maybeHide, 500);
            });
            $(this.el).mousemove(function (e) {
                mousepos = e;
            });
            // Showing the order list at the mouse postion
            $(this.el).mousestop(1000, function (e) {
                if (curTitle) {
                    orderList.$el[0].style.left = (mousepos.pageX + 10) + 'px';
                    orderList.$el[0].style.top = (mousepos.pageY - 50) + 'px';
                    if (curTitle != orderList.title) {
                        orderList.slice = curTitle;
                        orderList.typeFilter = curTitle;
                        orderList.addAll();
                    }
                }

            });

        },
        //not in used
        // planning to have an interaction between the progressbar and the order list
        handleClick: function (e) {
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
