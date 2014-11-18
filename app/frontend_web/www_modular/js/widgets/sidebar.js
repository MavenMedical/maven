/**
 * Created by devel on 11/16/14.
 */
define([
    // These are path alias that we configured in our main.js
    'jquery',     // lib/jquery/jquery
    'underscore', // lib/underscore/underscore
    'backbone',   // lib/backbone/backbone
    'globalmodels/contextModel'
], function ($, _, Backbone, contextModel) {


    var Sidebar = Backbone.View.extend({
        initialize: function (arg) {
            this.template = _.template(arg.template);
            this.render();
        },
        render: function(){
            this.$el.html(this.template());
        }

    });
    return Sidebar;
});