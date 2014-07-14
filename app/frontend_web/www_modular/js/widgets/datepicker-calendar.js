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
            var eventlist = [];

            for (var key in histogramModel.attributes) {
                var enc = histogramModel.attributes[key];
                eventlist.push({
                    id: enc['encounterid'],
                    title: enc['diagnosis'] + " $" + enc['spending'],
                    start: enc['admission'],
                    end: enc['discharge'],
                    className: 'admission'});
            }


            $('#calendar').fullCalendar({
                header: {
                    left: 'prev,next today',
                    center: 'title',
                    right: 'month,agendaWeek,agendaDay'
                },
                defaultDate: contextModel.get('enc_date'),

                eventClick: function (event) {
                    eventData = {
                        id: event.id,
                        title: event.title,
                        start: event.start,
                        end: event.end
                    }

                    var URL;

                    if (contextModel.get('patients')) {  // patient id must be available
                        URL = "episode/" + eventData['id'] + "/";
                        URL += "patient/" + contextModel.get('patients') + "/";
                        URL += eventData['start'].format();

                        // navigate to the chosen encounter
                        Backbone.history.navigate(URL, true);

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
