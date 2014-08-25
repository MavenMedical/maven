/**
 * Created by Asmaa Aljuhani on 3/11/14.
 */

define([
    // These are path alias that we configured in our main.js
    'jquery',     // lib/jquery/jquery
    'underscore', // lib/underscore/underscore
    'backbone',    // lib/backbone/backbone

     'text!templates/pathway/pathwaySearch.html'
], function ($, _, Backbone,  pathwaySearchTemplate) {
    
    var PathSearch = Backbone.View.extend({
        template: _.template(pathwaySearchTemplate),
	initialize: function(){
	    this.render();
	},
	render: function(){
        this.$el.html(this.template());
    }
    });
    return PathSearch;
});
