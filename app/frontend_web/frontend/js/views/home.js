/**
 * Created by Asmaa Aljuhani on 3/11/14.
 */

define([
    'jquery',     // lib/jquery/jquery
    'underscore', // lib/underscore/underscore
    'backbone',    // lib/backbone/backbone



    //views
    'views/widget/patientList',
    'views/chart/spending',
    'views/chart/costbd',

    // Using the Require.js text! plugin, we are loaded raw text
    // which will be used as our views primary template
    'text!templates/home.html'
], function ($, _, Backbone,PatientList, Spending, CostBD, homeTemplate ) {

    var HomeView = Backbone.View.extend({
        el: '.page',
        template: _.template(homeTemplate),
        initialize: function(){
            _.bindAll(this, 'render');
            this.render();
        },
        render: function () {
            $('.nav li').removeClass('active');
            $('.nav li a[href="' + window.location.hash + '"]').parent().addClass('active');
            $('.patientinfo').empty();

            this.$el.html(this.template);

            //widgets
            console.log('home render widgets');
            this.patientlistview = new PatientList;
            //console.log(patientlistview.patients);
            //$('.patientlist').append(patientlistview.render().el);
            this.spending = new Spending;
            this.costbd = new CostBD;

        }
    });

    return HomeView;

});