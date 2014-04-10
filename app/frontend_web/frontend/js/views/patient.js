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
        render: function () {
             $('.nav li').removeClass('active');
            $('.nav li a[href="' + window.location.hash + '"]').parent().addClass('active');

            var template = _.template(patientTemplate, {});
            this.$el.html(template);

            //widgets
            this.patinfo = new PatInfo;
            this.util = new Utilization;
            this.saving = new Saving;
            this.spending = new Spending;
            this.costbd = new CostBD;
            this.alert = new Alert;

            return this;
        }
    });

    return PatientView;

});