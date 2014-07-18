/**
 * Created by Asmaa Aljuhani on 7/5/14.
 */

define([
    // These are path alias that we configured in our main.js
    'jquery',     // lib/jquery/jquery
    'underscore', // lib/underscore/underscore
    'backbone',    // lib/backbone/backbone
    'fullcalendar',
    'globalmodels/contextModel',
    'globalmodels/histogramModel'
], function ($, _, Backbone, fullCalendar, contextModel, histogramModel) {
    var DatepickerCalendar = Backbone.View.extend({
        initialize: function (arg) {
            this.template = _.template(arg.template); // this must already be loaded
            this.$el.html(this.template({page: contextModel.get('page')}));
            contextModel.on('change:patients change:encounter change:enc_date', this.update, this);
            this.update();
            $("#datepicker-modal").on('shown.bs.modal', function () {
                $("#calendar").fullCalendar('render')
            });
        },
        update: function () {
            console.log('update calendar');
            var eventlist = [];

            for (var key in histogramModel.attributes) {
                var enc = histogramModel.attributes[key];
		var discharge = enc['discharge'];
		if (!discharge) {
		    discharge = (new Date()).toISOString().substring(0,10);
		}
                eventlist.push({
                    id: enc['encounterid'],
                    title: enc['patientname']+ ": "+ enc['diagnosis'] + " $" + enc['spending'],
                    start: enc['admission'],
                    end: discharge,
                    className: 'admission',
                    allDay: true,
                    url: "#episode/" + enc['encounterid'] + "/patient/" + enc['patientid'] + "/" + enc['admission'] });
            }


            $('#calendar').fullCalendar({
                header: {
                    left: 'prev,next',
                    center: 'title',
                    right: 'today'
                },
                defaultDate: contextModel.get('enc_date'),
                selectable: true,
                selectHelper: true,
                select: function (start, end, jsEvent) {
                    if (contextModel.get('patients')) {
                        contextModel.set({'enc':null, 'enc_date': null,
					  'startdate': start.format(),
					  'enddate': end.format()});
                        // navigate to the chosen encounter
                        Backbone.history.navigate("patient/" + contextModel.get('patients'), true);
                        // hide the modal
                        $('#datepicker-modal').modal('hide');
                    }
                    $('#calendar').fullCalendar('unselect');
                },

                eventClick: function (event) {
                    if (event.url) {
                        // navigate to the chosen encounter
                        Backbone.history.navigate(event.url, true);
                        // hide the modal
                        $('#datepicker-modal').modal('hide');

                    }
                },
                events: eventlist
            });
        }
    });
    return DatepickerCalendar;
});
