define([
    'jquery',     // lib/jquery/jquery
    'underscore', // lib/underscore/underscore
    'backbone',    // lib/backbone/backbone

    //views
    'globalmodels/alertCollection',
    
    'singleRow/alertRow',
    // Using the Require.js text! plugin, we are loaded raw text
    // which will be used as our views primary template
], function ($, _, Backbone, alertCollection, AlertRow) {

    var AlertList = Backbone.View.extend({
	initialize: function(arg) {
	    this.template = _.template(arg.template);
	    this.$el.html(this.template());
	    alertCollection.bind('add', this.addAlert, this);
	    alertCollection.bind('reset', this.reset, this);
	    //alertCollection.bind('remove', this.remove, this);
	    alertCollection.bind('sync', this.addAll, this);
	    this.addAll();
	},
	addAlert: function(alert) {
	    var alertrow = new AlertRow({model: alert});
	    $('#alertaccordion').append(alertrow.render().el);
	},	
	addAll: function() {
	    this.reset();
	    for(alert in alertCollection.models) {
		this.addAlert(alertCollection.models[alert]);
	    }
	},
	reset: function() {
	    $('#alertaccordion').empty();
	}
    });

    return AlertList;

});