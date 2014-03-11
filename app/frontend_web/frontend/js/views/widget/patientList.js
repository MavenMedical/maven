/**
 * Created by Asmaa Aljuhani on 3/11/14.
 */

define([
    // These are path alias that we configured in our main.js
    'jquery',     // lib/jquery/jquery
    'underscore', // lib/underscore/underscore
    'backbone',    // lib/backbone/backbone
    'text!templates/widget/patientList.html'
], function ($, _, Backbone, patientListTemplate) {

    var PatientList = Backbone.View.extend({
        el: $('.patientlist'),
        render: function () {
            var template = _.template(patientListTemplate, {});
            $('.patientlist').append(template);
        }
    });
    return PatientList;
});
