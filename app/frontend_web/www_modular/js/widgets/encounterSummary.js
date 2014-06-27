/**
 * Created by Asmaa Aljuhani on 3/11/14.
 */

define([
    // These are path alias that we configured in our main.js
    'jquery',     // lib/jquery/jquery
    'underscore', // lib/underscore/underscore
    'backbone',    // lib/backbone/backbone
    'datepicker',
    'globalmodels/summaryModel', // current patient (if any)
    'globalmodels/patientModel',
    'globalmodels/contextModel',
    'globalmodels/histogramModel'
], function ($, _, Backbone, datepicker, summaryModel, patientModel, contextModel, histogramModel) {

    var Summary = Backbone.View.extend({
        initialize: function (arg) {
            this.template = _.template(arg.template); // this must already be loaded
            this.update(summaryModel);
            summaryModel.on('change', this.update, this);
            contextModel.on('change:patients change:encounter', this.update, this);
            patientModel.on('change:name', this.update, this);

            // Source for Date picker http://bootstrap-datepicker.readthedocs.org/en/release/index.html
            $('#datepicker').datepicker({
                format: "mm/dd/yyyy",
                autoclose: true,
                endDate: new Date(), //calender end date is today
                beforeShowDay: function (date) {
                    for (var key in histogramModel.attributes) {
                        var enc = histogramModel.attributes[key];
                        if(date.setHours(0, 0, 0, 0) == new Date(enc['admission']).setHours(0, 0, 0, 0)){
                           return {
                                tooltip: 'Encounter Cost $'+enc['spending'],
                                classes: 'admission'
                           }
                            //TODO: add the css class for all days between the admission and discharge
                        }else{
                            return false;
                        }
                    }
                }
            })
                .on('changeDate', function (e) {
                    console.log('date change');
                    console.log(e);
                    console.log(e.date.toLocaleDateString()); //get picked Date
                    contextModel.set({enc_date:e.date.toLocaleDateString()});
                    console.log(contextModel.attributes);
                });

            $('#datepicker').datepicker('update', new Date('2014-03-24')); // set the encounter date here
        },
        update: function (summary) {
            if (summaryModel.get('spending')) {
                var title = 'your patients';
                if (contextModel.get('encounter')) {
                    title = 'current encounter';
                } else if (patientModel.get('name')) {
                    title = patientModel.get('name');
                }
                this.$el.html(this.template($.extend({}, summaryModel.attributes, {'title': title})));
                this.$el.show();
            } else {
                this.$el.hide();
            }
        }
    });
    return Summary;
})
;
