/**
 * Created by Asmaa Aljuhani on 3/11/14.
 */

define([
    // These are path alias that we configured in our main.js
    'jquery',     // lib/jquery/jquery
    'underscore', // lib/underscore/underscore
    'backbone',    // lib/backbone/backbone
    'currentContext',
    'text!templates/topnav.html'
	], function ($, _, Backbone, currentContext, topnavTemplate) {

    var TopNav = Backbone.View.extend({
        el: $('.topnav'),
        render: function () {
		var template = _.template(topnavTemplate, currentContext.attributes);
            this.$el.html(template);
            return this;
        }
    });
    return TopNav;
});
