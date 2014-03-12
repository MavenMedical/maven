/**
 * Created by Asmaa Aljuhani on 3/11/14.
 */

define([
    // These are path alias that we configured in our main.js
    'jquery',     // lib/jquery/jquery
    'underscore', // lib/underscore/underscore
    'backbone',    // lib/backbone/backbone
    'text!templates/widget/alert.html'
], function ($, _, Backbone, alertTemplate) {

    var Alert = Backbone.View.extend({
        el: $('.alert'),
        render: function () {
            var template = _.template(alertTemplate, {});
            $('.alert').append(template);
        }
    });
    return Alert;
});
