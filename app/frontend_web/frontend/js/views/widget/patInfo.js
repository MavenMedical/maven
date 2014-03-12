/**
 * Created by Asmaa Aljuhani on 3/11/14.
 */

define([
    // These are path alias that we configured in our main.js
    'jquery',     // lib/jquery/jquery
    'underscore', // lib/underscore/underscore
    'backbone',    // lib/backbone/backbone
    'text!templates/widget/patInfo.html'
], function ($, _, Backbone, patInfoTemplate) {

    var PatInfo = Backbone.View.extend({
        el: $('.patientinfo'),
        render: function () {
            var template = _.template(patInfoTemplate, {});
            $('.patientinfo').empty();
            $('.patientinfo').append(template);
        }
    });
    return PatInfo;
});
