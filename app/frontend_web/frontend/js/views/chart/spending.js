/**
 * Created by Asmaa Aljuhani on 3/11/14.
 */

define([
    // These are path alias that we configured in our main.js
    'jquery',     // lib/jquery/jquery
    'underscore', // lib/underscore/underscore
    'backbone',    // lib/backbone/backbone
    'currentContext',
    //model
    'models/chartsModels/spendingModel',
    'text!templates/chart/spending.html'
	], function ($, _, Backbone, currentContext, SpendingModel, spendingTemplate) {

    var Spending = Backbone.View.extend({
        el: '.spending',
        template: _.template(spendingTemplate),
        initialize: function () {
            _.bindAll(this, 'render');
            this.spend = new SpendingModel;
            this.render();
        },
        render: function () {
            console.log('spending');
            var that = this;
            this.spend.fetch({
                success: function (spend) {
                    patientName = currentContext.get('patientName');
                    if (!patientName) {
                        patientName = 'All Patients';
                    }

                    that.$el.html(that.template({spending: spend, patientName: patientName,
				    display:currentContext.get('display')}));
                },
                data: $.param(currentContext.toJSON())
            });
            return this;
        }
    });
    return Spending;
});
//Chart codes are in the template file spending.html