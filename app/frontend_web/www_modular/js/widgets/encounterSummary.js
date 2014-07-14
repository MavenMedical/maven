/**
 * Created by Asmaa Aljuhani on 3/11/14.
 */

define([
    // These are path alias that we configured in our main.js
    'jquery',     // lib/jquery/jquery
    'underscore', // lib/underscore/underscore
    'backbone',    // lib/backbone/backbone
    'globalmodels/summaryModel', // current patient (if any)
    'globalmodels/patientModel',
    'globalmodels/contextModel',
], function ($, _, Backbone, summaryModel, patientModel, contextModel) {

    var Summary = Backbone.View.extend({
        initialize: function (arg) {
            this.template = _.template(arg.template); // this must already be loaded
            this.update(summaryModel);
            summaryModel.on('change', this.update, this);
            contextModel.on('change:patients change:encounter change:enc_date', this.update, this);
            patientModel.on('change:name', this.update, this);



        },
        update: function (summary) {
            var title = 'your patients';
	    var date = contextModel.get('enc_date');
            if (contextModel.get('encounter')) {
                title = 'encounter including ' + date;;
            } else if (patientModel.get('name')) {
                title = patientModel.get('name');
            }
            $('#datepicker-input').val(date);
	    
            this.$el.html(this.template($.extend({}, summaryModel.attributes, {'title': title})));
        }
    });
    return Summary;
})
;
