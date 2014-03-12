/**
 * Created by Asmaa Aljuhani on 3/11/14.
 */

define([
    // These are path alias that we configured in our main.js
    'jquery',     // lib/jquery/jquery
    'underscore', // lib/underscore/underscore
    'backbone',    // lib/backbone/backbone
    'text!templates/widget/orderable.html'
], function ($, _, Backbone, orderableTemplate) {

    var Orderable = Backbone.View.extend({
        el: $('.orderable'),
        render: function () {
            var template = _.template(orderableTemplate, {});
            $('.orderable').append(template);
        }
    });
    return Orderable;
});
