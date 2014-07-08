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

            var eventlist = [];

            for (var key in histogramModel.attributes) {
                var enc = histogramModel.attributes[key];
                eventlist.push({id: null,
                    title: enc['diagnosis'] + " $" + enc['spending'],
                    start: enc['admission'],
                    end: "2014-03-29", //enc['discharge'],
                    className: 'admission'});
                console.log(enc['admission']);
            }


            $('.popper').popover({
                placement: 'right',//'bottom',
                container: 'body',
                html: true,
                content: function () {
                    return $('#calendar').fullCalendar({
                        theme: true,
                        header: {
                            left: 'prev',
                            center: 'title',
                            right: 'next'
                        },
                        selectable: true,
                       // selectHelper: true,

                        defaultDate: contextModel.get('enc_date'),
                        //editable: false,
                        events: eventlist

                    });
                }
            });

        },
        update: function () {
        }
    });
    return DatepickerCalendar;
});
