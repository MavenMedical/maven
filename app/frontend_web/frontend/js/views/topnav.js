/**
 * Created by Asmaa Aljuhani on 3/11/14.
 */

define([
    // These are path alias that we configured in our main.js
    'jquery',     // lib/jquery/jquery
    'underscore', // lib/underscore/underscore
    'backbone',    // lib/backbone/backbone
    'currentContext',
    'text!templates/templatesA/topnav.html',
    'text!templates/templatesB/topnav.html'
	], function ($, _, Backbone, currentContext, topnavTemplateA,topnavTemplateB ) {

    var TopNav = Backbone.View.extend({
        el: '.topnav',
        initialize: function(){
            this.render();
            alert(currentContext.get('layout'));
        },
        render: function () {
		var template = _.template(topnavTemplateA, currentContext.attributes);
		this.$el.html(template);
		return this;
        }
    });
    return TopNav;
});
