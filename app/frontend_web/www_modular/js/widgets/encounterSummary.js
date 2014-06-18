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
], function ($, _, Backbone, datepicker, summaryModel, patientModel, contextModel) {

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
            })
                .on('changeDate', function (e) {
                    console.log('date change');
                    console.log(e.date.toLocaleDateString()); //get picked Date
                });

           // $('#datepicker').datepicker('update', new Date()); // set the encounter date here
        },
        update: function (summary) {
            if (summaryModel.get('spending')) {
                var title = 'your patients';
                if (contextModel.get('encounter')) {
                    title = 'current encounter';
                } else if (patientModel.get('name')) {
                    title = patientModel.get('name');
                }
                //console.log(title+": "+contextModel.get('encounter')+"  "+contextModel.get('patients'));
                //console.log(contextModel);
                this.$el.html(this.template($.extend({}, summaryModel.attributes, {'title': title})));
                this.$el.show();
            } else {
                this.$el.hide();
            }
        }
    });
    return Summary;
});
