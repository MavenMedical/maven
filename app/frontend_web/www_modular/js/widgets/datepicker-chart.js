/**
 * Created by Asmaa Aljuhani on 7/5/14.
 */

define([
    // These are path alias that we configured in our main.js
    'jquery',     // lib/jquery/jquery
    'underscore', // lib/underscore/underscore
    'backbone',    // lib/backbone/backbone
    'globalmodels/contextModel',
    'globalmodels/histogramModel'
], function ($, _, Backbone, contextModel, histogramModel) {

    var DatepickerChart = Backbone.View.extend({
        initialize: function (arg) {
            this.template = _.template(arg.template); // this must already be loaded
            histogramModel.on('change', this.update, this);
            contextModel.on('change page', this.update, this);

            console.log(histogramModel.attributes);
            this.$el.html(this.template(this));
            this.update();
        },
        update: function () {

            var data = [];
            for (var key in histogramModel.attributes) {
                var enc = histogramModel.attributes[key];
                data.push(enc);
            }

            var chart = AmCharts.makeChart("datepicker-chart", {

                "type": "serial",
                "theme": "light",
                "pathToImages": "http://cdn.amcharts.com/lib/3/images/",
                "categoryField": "admission",
                "startDuration": 1,
                "categoryAxis": {
                    "gridPosition": "start"
                },
                "chartCursor": {},
                "chartScrollbar": {},
                "trendLines": [],
                "graphs": [
                    {
                        "fillAlphas": 1,
                        "id": "AmGraph-1",
                        "title": "graph 1",
                        "type": "column",
                        "valueField": "spending"
                    }
                ],
                "guides": [],
                "valueAxes": [
                    {
                        "id": "ValueAxis-1",
                        "title": "Spending"
                    }
                ],
                "allLabels": [],
                "balloon": {
                },

                "dataProvider": data
            });

            chart.addListener("clickGraphItem", function(e){
                var eventData = e.item.dataContext ;

                console.log(eventData);

                var URL;

                    if (contextModel.get('patients')) {  // patient id must be available
                        URL = "episode/" + eventData['id'] + "/";
                        URL += "patient/" + contextModel.get('patients') + "/";
                        URL += eventData['admission'];

                        // navigate to the chosen encounter
                        Backbone.history.navigate(URL, true);

                        // hide the modal
                        $('#datepicker-modal').modal('hide');
                    }

            });
	    $("#datepicker-modal").on('shown.bs.modal', function() {chart.invalidateSize();});
	    
        }
    });
    return DatepickerChart;
});
