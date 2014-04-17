/**
 * Created by Asmaa Aljuhani on 3/11/14.
 */

define([
    'jquery',     // lib/jquery/jquery
    'underscore', // lib/underscore/underscore
    'backbone',    // lib/backbone/backbone
    'currentContext',
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
], function ($, _, Backbone, currentContext, PatientModel, PatInfo, Utilization, Saving, Alert, Spending, CostBD, patientTemplate) {

    var PatientView = Backbone.View.extend({
        el: $('.page'),
        render: function () {
            $('.nav li').removeClass('active');
            //add patient li to the large side menu
            $('#dynamic_menu').append(
                $('<li>').attr('class', 'active').append(
                    $('<a>').attr('href', '#/patient').append(
                        $('<i>').attr('class', 'glyphicon glyphicon-user').append(
                            $('<span>').append(' Patient (' + currentContext.get('patientName') + ')')
                        ))));

            //TODO this should be generated from real data from DB
            //append list of encounters
            var enc = ['1/4/2014', '2/3/2014', '12/17/2013'];
            for (var i = 0; i < enc.length; i++) {
                $('#dynamic_menu').append(
                    $('<li>').append(
                        $('<a>').attr('href', '#/episode/9|76|3140328/patient/9').append(
                            $('<i>').attr('class', 'glyphicon glyphicon-time').append(
                                $('<span>').append(' Encounter (' + enc[i] + ')')))));

            }


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