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
    // This view is to render a date picker in a modal
    // Datepicker uses two calendar and shows encounters
    // each encounter has a start date and end date , some encounters are one day long
    // encounters are shown on the calendar as events
    //Another datepicker visialization is datepicker-chart
    var DatepickerCalendar = Backbone.View.extend({
        initialize: function (arg) {
            this.template = _.template(arg.template); // this must already be loaded
            this.$el.html(this.template({page: contextModel.get('page')}));
            contextModel.on('change:patients change:encounter change:enc_date', this.update, this);
            this.update();
            //showing 2 calendars in this modal
            // the second calendar shows the following month to the first calendar
            $("#datepicker-modal").on('shown.bs.modal', function () {
                $("#calendar1").fullCalendar('render');
                $("#calendar2").fullCalendar('render');
            });
        },
        events: {
            'click .btn': 'showEncounters' // clicking on an encounter event would update the page content
        },
        update: function () {
            //using fullCalender library
            var calendar = new Array();
            //using two calender to get better view of the encounters
            var num_of_calendars = 2;
            var eventlist = [];

            for (var key in histogramModel.attributes) {
                var enc = histogramModel.attributes[key];
                var discharge = enc['discharge'];
                if (!discharge) { // means its a one day encounter
                    discharge = (new Date()).toISOString().substring(0, 10);
                }
                //adding data to eventlist array
                eventlist.push({
                    id: enc['encounterid'],
                    // displayed info are (patient name, diagnosis, and he amount of money spent in that encounter)
                    title: enc['patientname'] + ": " + enc['diagnosis'] + " $" + enc['spending'],
                    start: enc['admission'],
                    end: discharge,
                    className: 'admission',
                    allDay: true,
                    // when clicking on an event it will navigate to the clicked encounter
                    url: "#episode/" + enc['encounterid'] + "/patient/" + enc['patientid'] + "/" + enc['admission'] });
            }

            for (var i = 1; i <= num_of_calendars; i++) {
                var today = new Date ();
                // if there is a selected encounter date otherwise select today's date
                var d = (contextModel.get('enc_date'))? new Date(contextModel.get('enc_date')): new Date(today.getFullYear(), today.getMonth() - 2, 1);
                // second calendar showing the following month of the first calendar
                var dd = d.setMonth(d.getMonth() + i);
                //header of the calendar shows these buttons
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
                    // upon clicking on an event it will navigate to the desired encounter
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
            // having both calendars interact together
            // clicking on prev would shows the previouse moth on both calendars
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
