/**
 * Created by Asmaa Aljuhani on 3/11/14.
 */

define([
    'jquery',     // lib/jquery/jquery
    'underscore', // lib/underscore/underscore
    'backbone',    // lib/backbone/backbone

    //Model
    'models/patientModel',

    //Collection
    'collections/patients',

    //views
    'views/widget/patientList',
    'views/chart/spending',
    'views/chart/costbd',

    // Using the Require.js text! plugin, we are loaded raw text
    // which will be used as our views primary template
    'text!templates/home.html'
], function ($, _, Backbone, PatientModel, PatientCollection, PatientList, Spending, CostBD, homeTemplate) {

    var HomeView = Backbone.View.extend({
        el: $('.page'),
        render: function () {
            $('.nav li').removeClass('active');
            $('.nav li a[href="' + window.location.hash + '"]').parent().addClass('active');

            var template = _.template(homeTemplate, {});
            this.$el.html(template);

            //widgets
            var patientcollection = new PatientCollection();

            var patientlistview = new PatientList({collection: patientcollection});
            patientlistview.render();

            var spending = new Spending;
           spending.render();

            var costbd = new CostBD;
            costbd.render();
        }
    });

    return HomeView;

});