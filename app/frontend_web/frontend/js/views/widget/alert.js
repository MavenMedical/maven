/**
 * Created by Asmaa Aljuhani on 3/11/14.
 */

define([
    // These are path alias that we configured in our main.js
    'jquery',     // lib/jquery/jquery
    'underscore', // lib/underscore/underscore
    'backbone',    // lib/backbone/backbone
    'collections/alerts',
    'text!templates/widget/alert.html'
	], function ($, _, Backbone, AlertCollection, alertTemplate) {

    var Alert = Backbone.View.extend({
        el: $('.alertlist'),
        render: function () {
		var alertCollection = new AlertCollection();

		alertCollection.fetch({
			success: function(alerts) {
			    var template = _.template(alertTemplate, {alerts: alerts.models});
			    this.$('.alertlist').append(template);
			    //this.$('.alertlist').append("OTHER TEXT");
			},
			    data: $.param({user:'tom'})
			    });
        }
    });
    return Alert;
});
