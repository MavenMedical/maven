/**
 * Created by Asmaa Aljuhani on 3/11/14.
 */

define([
  'jquery',     // lib/jquery/jquery
  'underscore', // lib/underscore/underscore
  'backbone',    // lib/backbone/backbone

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
], function($, _, Backbone, PatInfo, Utilization, Saving, Alert, Spending, CostBD, patientTemplate){

    var PatientView = Backbone.View.extend({
        el: $('.page'),
        render: function(){
            $('.nav li').removeClass('active');
            $('.nav li a[href="'+window.location.hash+'"]').parent().addClass('active');

           var template = _.template(patientTemplate, {});
           this.$el.html(template);

            //widgets
            var patinfo = new PatInfo;
            patinfo.render();

            var util = new Utilization;
            util.render();

            var saving = new Saving;
            saving.render();

            var spending = new Spending;
            spending.render();

            var costbd = new CostBD;
            costbd.render();

            var alert = new Alert;
            alert.render();

        }
    });

    return PatientView;

});