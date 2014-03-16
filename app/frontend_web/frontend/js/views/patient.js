/**
 * Created by Asmaa Aljuhani on 3/11/14.
 */

define([
    'jquery',     // lib/jquery/jquery
    'underscore', // lib/underscore/underscore
    'backbone',    // lib/backbone/backbone
    //models
    'models/patientModel',

    //views
    'views/widget/patInfo',
    'views/widget/utilization',
    'views/widget/saving',
    'views/widget/alert',

    'views/chart/spending',
    'views/chart/costbd',

    // Using the Require.js text! plugin, we are loaded raw text
    // which will be used as our views primary template
    'text!templates/patient.html'
], function ($, _, Backbone, PatientModel, PatInfo, Utilization, Saving, Alert, Spending, CostBD, patientTemplate) {

    var PatientView = Backbone.View.extend({
        el: $('.page'),
        render: function (patid) {

            var template = _.template(patientTemplate, {});
            this.$el.html(template);

            //widgets
            var patinfo = new PatInfo;
            patinfo.render(patid);

            var util = new Utilization;
            util.render(patid);

            var saving = new Saving;
            saving.render(patid);

            var spending = new Spending;
            spending.render(patid);

            var costbd = new CostBD;
            costbd.render(patid);

            var alert = new Alert;
            alert.render(patid);

        }
    });

    return PatientView;

});