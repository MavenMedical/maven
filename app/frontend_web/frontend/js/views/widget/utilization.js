/**
 * Created by Asmaa Aljuhani on 3/11/14.
 */

define([
    // These are path alias that we configured in our main.js
    'jquery',     // lib/jquery/jquery
    'underscore', // lib/underscore/underscore
    'backbone',    // lib/backbone/backbone
    'currentContext',
    'text!templates/widget/utilization.html'
], function ($, _, Backbone, currentContext, utilizationTemplate) {

    var Utilization = Backbone.View.extend({
        el: '.utilization',
        template: _.template(utilizationTemplate),
        initialize: function(){
            _.bindAll(this,'render');
            this.render();
        },
        render: function () {
            this.$el.html(this.template({page: currentContext.page}));
        }
    });
    return Utilization;
});
