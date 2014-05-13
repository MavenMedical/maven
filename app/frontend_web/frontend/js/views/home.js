/**
 * Created by Asmaa Aljuhani on 3/11/14.
 */

define([
    'jquery',     // lib/jquery/jquery
    'underscore', // lib/underscore/underscore
    'backbone',    // lib/backbone/backbone

    // models
    'currentContext',
    'models/chartsModels/spendingModel',

    //views
    'views/widget/search',
    'views/widget/patientList',
    'views/chart/spending',
    'views/chart/costbd',

    // Using the Require.js text! plugin, we are loaded raw text
    // which will be used as our views primary template
    'text!templates/home.html'
	], function ($, _, Backbone, currentContext, SpendingModel, Search, PatientList, Spending, CostBD, homeTemplate ) {

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
             // clear li content from the dynamic list
            $('#dynamic_pat li').remove();
            $('#dynamic_enc li').remove();
            $('#dynamic_menu_xs').empty();
            $('.patientinfo').empty();

            this.$el.html(this.template);

            //widgets
            console.log('home render widgets');
            this.search = new Search;
            this.patientlist = new PatientList;
            console.log('home widgets');
            console.log(currentContext);
            this.spendingModel = new SpendingModel;
            this.spending = new Spending;
            this.costbd = new CostBD;
            this.spendingModel.on('change', this.spending.update);
            this.spendingModel.on('change', this.costbd.update);
            this.spendingModel.fetch({data: $.param(currentContext.toJSON())});
            return this;
        }
    });

    return HomeView;

});