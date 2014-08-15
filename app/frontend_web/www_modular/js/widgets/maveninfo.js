/**
 * Created by Asmaa Aljuhani on 8/8/14.
 */

define([
    // These are path alias that we configured in our main.js
    'jquery',     // lib/jquery/jquery
    'underscore', // lib/underscore/underscore
    'backbone',    // lib/backbone/backbone
    'globalmodels/contextModel'
], function ($, _, Backbone, contextModel) {
    var MavenInfo = Backbone.View.extend({
        initialize: function (arg) {
            this.template = _.template(arg.template);
            console.log('maveninfo ini');
            this.$el.html(this.template());
            //this.render();
        },
        events: {

        },
        render: function () {

        }
    });
    return MavenInfo;
});