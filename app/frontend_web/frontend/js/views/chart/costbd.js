/**
 * Created by Asmaa Aljuhani on 3/11/14.
 */

define([
    // These are path alias that we configured in our main.js
    'jquery',     // lib/jquery/jquery
    'underscore', // lib/underscore/underscore
    'backbone',    // lib/backbone/backbone

    'text!templates/chart/costbd.html'
], function ($, _, Backbone, costbdTemplate) {

    var CostBD = Backbone.View.extend({
        el: $('.costbd'),
        render: function () {

   var template = _.template(costbdTemplate, {});
            $('.costbd').append(template);
        }
    });
    return CostBD;
});
