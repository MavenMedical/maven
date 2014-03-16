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
        render: function (patid) {

            $('.nav li').removeClass('active');
            $('.nav li a[href="' + window.location.hash + '"]').parent().addClass('active');

            var pat = new PatientModel();
            console.log(pat);
            /*
            pat.fetch({
                success: function (pat) {
                    console.log("fetch patient collection success");
                    console.log(pat);
                    var template = _.template(patientTemplate, {patient:pat});
                    this.$el.html(template);
                },
                data: $.param({ user: 'tom', patient: patid})
            });
            */



            var template = _.template(patInfoTemplate, {});
            $('.patientinfo').empty();
            $('.patientinfo').append(template);
        }
    });
    return PatInfo;
});
