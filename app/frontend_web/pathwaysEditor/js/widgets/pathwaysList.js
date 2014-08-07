/**
 * Created by Asmaa Aljuhani on 8/7/14.
 */

define([
    // These are path alias that we configured in our main.js
    'jquery',     // lib/jquery/jquery
    'underscore', // lib/underscore/underscore
    'backbone',    // lib/backbone/backbone

     'text!templates/pathwaysList.html'
], function ($, _, Backbone,  pathwaysListTemplate) {

    var PathwaysList = Backbone.View.extend({
        template: _.template(pathwaysListTemplate),
	initialize: function(){
	    this.render();
	},
	render: function(){
        this.$el.html(this.template());
    }
    });
    return PathwaysList;
});
