/**
 * Created by Asmaa Aljuhani on 3/11/14.
 */


define([
    // These are path alias that we configured in our main.js
    'jquery',     // lib/jquery/jquery
    'underscore', // lib/underscore/underscore
    'backbone',    // lib/backbone/backbone
    'text!templates/templatesA/sidemenu.html'
], function ($, _, Backbone, sidemenuTemplate) {

    var SideMenu = Backbone.View.extend({
	    el: '.sidemenu',
        render: function () {
            var template = _.template(sidemenuTemplate, {});
            this.$el.html(template);
            return this;
        }
    });
    return SideMenu;
});
