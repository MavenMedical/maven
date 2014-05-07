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
    'models/chartsModels/spendingModel',
    //views
    'views/widget/patInfo',
    'views/widget/utilization',
    'views/widget/saving',
    'views/widget/alert',

    'views/chart/spending',
    'views/chart/costbd',
    'views/chart/costbdlist',

    // Using the Require.js text! plugin, we are loaded raw text
    // which will be used as our views primary template
    'text!templates/patient.html'
	], function ($, _, Backbone, currentContext, PatientModel, SpendingModel, PatInfo, Utilization, Saving, Alert, Spending, CostBDDonut, CostBDList, patientTemplate) {

    var PatientView = Backbone.View.extend({
        el: $('.page'),
        render: function () {
            $('.nav li').removeClass('active');
            $('#dynamic_pat li').remove();
            $('#dynamic_enc li').remove();

            //add patient li to the large side menu
            $('#dynamic_pat').append(
                $('<li>').attr('class', 'active').append(
                    $('<a>').attr('href', '#/patient').append(
                        $('<i>').attr('class', 'glyphicon glyphicon-user').append(
                            $('<span>').append(' Patient (' + currentContext.get('patientName') + ')')
                        ))));

            //TODO this should be generated from real data from DB
            //append list of encounters
            var enc = ['1/4/2014', '2/3/2014', '12/17/2013'];
            for (var i = 0; i < enc.length; i++) {
                $('#dynamic_enc').append(
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
	    if(currentContext.get('costbdtype') == 'donut') {
		this.costbd = new CostBDDonut;
	    } else {
		this.costbd = new CostBDList;
	    };
            this.alert = new Alert;

            this.spendingModel = new SpendingModel;
            this.spendingModel.on('change', this.spending.update);
            this.spendingModel.on('change', this.costbd.update);
            this.spendingModel.fetch({data: $.param(currentContext.toJSON())});

            return this;
        }
    });

    return PatientView;

});