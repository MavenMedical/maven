/**
 * Created by Asmaa Aljuhani on 3/11/14.
 */

define([
    // These are path alias that we configured in our main.js
    'jquery',     // lib/jquery/jquery
    'underscore', // lib/underscore/underscore
    'backbone',    // lib/backbone/backbone


    //Model
    'models/patientModel',

    //Collection
    'collections/patients',

    //Template
    'text!templates/widget/patientList.html'
], function ($, _, Backbone, PatientModel, PatientCollection, patientListTemplate) {

    var PatientList = Backbone.View.extend({
        el: $('.patientlist'),

        render: function () {
            console.log("render in patient List ");
            var patients = new PatientCollection();
             console.log("render in patient List after creating collection");

            patients.fetch({
                success: function (patients) {
                    console.log("fetch patient collection success");
                    console.log(patients);
                    var template = _.template(patientListTemplate, {patients: patients.models});
                    this.$('.patientlist').append(template);
                },
                data: $.param({ user: 'tom'})
            });

        }
    });
    return PatientList;
});
