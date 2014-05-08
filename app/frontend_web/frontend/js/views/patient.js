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
	update: function(patientModel) {
            //append list of encounters
            $('#dynamic_enc li').remove();
            var enc = patientModel.get('encounters');
	    var pat_id = patientModel.get('id');
            for (var i = 0; i < enc.length; i++) {
                $('#dynamic_enc').append(
                    $('<li>').append(
                        $('<a>').attr('href', '#/episode/'+enc[i][0]+'/patient/'+pat_id).append(
                            $('<i>').attr('class', 'glyphicon glyphicon-time').append(
                                $('<span>').append(' Encounter (' + enc[i][1] + ')')))));

            }
	    },
        render: function () {
            $('.nav li').removeClass('active');
            $('#dynamic_pat li').remove();

            //add patient li to the large side menu
            $('#dynamic_pat').append(
                $('<li>').attr('class', 'active').append(
                    $('<a>').attr('href', '#/patient').append(
                        $('<i>').attr('class', 'glyphicon glyphicon-user').append(
                            $('<span>').append(' Patient (' + currentContext.get('patientName') + ')')
                        ))));

            var template = _.template(patientTemplate, {});
            this.$el.html(template);

	    var that=this;
            //widgets
	    this.patientModel = new PatientModel;
            this.patinfo = new PatInfo;
	    this.patientModel.on('change', function(pat) {that.patinfo.update(that.patinfo, pat)});
	    this.patientModel.on('change', this.update);
	    this.patientModel.fetch({data:$.param(currentContext.toJSON())});
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