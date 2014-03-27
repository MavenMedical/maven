/**
 * Created by Asmaa Aljuhani on 3/14/14.
 */

define([
    'underscore',
    'backbone'
], function (_, Backbone) {

    var PatientModel = Backbone.Model.extend({
        urlRoot: '/patient_details',
        defaults: {
            name: "Batman",
            gender: "Male",
            DOB: "05/03/1987",
            dx: "Asthma",
            cost: "$1200"
        }
    });

    return PatientModel;

});