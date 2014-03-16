/**
 * Created by Asmaa Aljuhani on 3/11/14.
 */

define([
    // These are path alias that we configured in our main.js
    'jquery',     // lib/jquery/jquery
    'underscore', // lib/underscore/underscore
    'backbone',    // lib/backbone/backbone

    'text!templates/chart/spending.html'
], function ($, _, Backbone,  spendingTemplate) {

    var Spending = Backbone.View.extend({
        el: $('.spending'),
        render: function () {
            var template = _.template(spendingTemplate, {});
            $('.spending').append(template);
        }
    });
    return Spending;
});
