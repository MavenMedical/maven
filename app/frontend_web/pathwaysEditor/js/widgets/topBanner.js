/**
 * Created by Asmaa Aljuhani on 3/11/14.
 */

define([
    // These are path alias that we configured in our main.js
    'jquery',     // lib/jquery/jquery
    'underscore', // lib/underscore/underscore
    'backbone',   // lib/backbone/backbone

    'text!templates/topBanner.html'
], function ($, _, Backbone, topBannerTemplate) {

    var TopBanner = Backbone.View.extend({
        template: _.template(topBannerTemplate),
        initialize: function () {
            this.render();
        },
        render: function(){
            this.$el.html(this.template());
        }

    });
    return TopBanner;
});
