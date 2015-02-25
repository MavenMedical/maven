/**
 * Created by Asmaa Aljuhani on 3/11/14.
 */

define([
    // These are path alias that we configured in our main.js
    'jquery',     // lib/jquery/jquery
    'underscore', // lib/underscore/underscore
    'backbone',    // lib/backbone/backbone
    'globalmodels/patientModel', // current patient (if any)
    'globalmodels/contextModel',
], function ($, _, Backbone,  patientModel, contextModel) {
    
    var PatInfo = Backbone.View.extend({
	initialize: function(arg) {
        this.template = _.template(arg.template);
        this.update(patientModel);
        patientModel.on('change', this.update, this);
        contextModel.on('change:page', function(){
            if (contextModel.get('page')=='pathway'){
                this.update(patientModel);
            } else {
                this.$el.hide();
            }
        }, this);
    },
	update: function(pat) {
	    if(patientModel.get('id') && contextModel.get('page') == 'pathway') {
            this.$el.html(this.template(patientModel.attributes));
            this.$el.show();
	    } else {
            // for now we just hide this if no patient is selected
            this.$el.hide();
	    }
	}
    });
    return PatInfo;
});
