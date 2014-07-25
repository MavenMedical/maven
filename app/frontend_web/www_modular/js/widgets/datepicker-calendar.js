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
                $("#calendar1").fullCalendar('render');
                $("#calendar2").fullCalendar('render');

            });
        },
        events: {
            'click .btn': 'showEncounters'
        },
        update: function () {

            var calendar = new Array();
            var num_of_calendars = 2;
            var eventlist = [];

            for (var key in histogramModel.attributes) {
                var enc = histogramModel.attributes[key];
                var discharge = enc['discharge'];
                if (!discharge) {
                    discharge = (new Date()).toISOString().substring(0, 10);
                }
                eventlist.push({
                    id: enc['encounterid'],
                    title: enc['patientname'] + ": " + enc['diagnosis'] + " $" + enc['spending'],
                    start: enc['admission'],
                    end: discharge,
                    className: 'admission',
                    allDay: true,
                    url: "#episode/" + enc['encounterid'] + "/patient/" + enc['patientid'] + "/" + enc['admission'] });
            }

            for (var i = 1; i <= num_of_calendars; i++) {
                var today = new Date ();
                var d = (contextModel.get('enc_date'))? new Date(contextModel.get('enc_date')): new Date(today.getFullYear(), today.getMonth() - 2, 1);
                var dd = d.setMonth(d.getMonth() + i);
                calendar[i] = $("#calendar" + i).fullCalendar({
                    header: {
                        left: (i == 1) ? 'prev,next' : '',
                        center: 'title',
                        right: (i == 2) ? 'today' : ''
                    },
                    defaultDate: dd,
                    selectable: true,
                    selectHelper: true,
                    select: function (start, end, jsEvent) {
                        if (contextModel.get('patients')) {
                            contextModel.set({'enc': null, 'enc_date': null,
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

            $("#calendar1 .fc-button-prev").each(function () {
                $(this).click(function () {
                    $("#calendar2").each(function () {
                        $(this).fullCalendar('prev');
                    });
                });
            });
            $("#calendar1 .fc-button-next").each(function () {
                $(this).click(function () {
                    $("#calendar2").each(function () {
                        $(this).fullCalendar('next');
                    });
                });
            });
            $("#calendar2 .fc-button-today").each(function () {
                $(this).click(function () {
                    $("#calendar1").each(function () {
                        $(this).fullCalendar('today');
                        $(this).fullCalendar('prev');
                    });
                });
            });
        },
        showEncounters: function (e) {
            var period = e.target.id;
            var d = new Date();
            d.setMonth(d.getMonth() - period);
            console.log(d.toLocaleDateString());

            contextModel.set({'enc': null, 'enc_date': null,
                'startdate': d.toLocaleDateString(),
                'enddate': (new Date()).toLocaleDateString()});
            // navigate to the chosen encounter
            Backbone.history.navigate("patient/" + contextModel.get('patients'), true);
            // hide the modal
            $('#datepicker-modal').modal('hide');
        }
    });
    return DatepickerCalendar;
});
