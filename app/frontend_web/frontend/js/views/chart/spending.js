/**
 * Created by Asmaa Aljuhani on 3/11/14.
 */

define([
    // These are path alias that we configured in our main.js
    'jquery',     // lib/jquery/jquery
    'underscore', // lib/underscore/underscore
    'backbone',    // lib/backbone/backbone
    //model
    'models/chartsModels/spendingModel',

    'text!templates/chart/spending.html'
], function ($, _, Backbone, SpendingModel, spendingTemplate) {

    var Spending = Backbone.View.extend({
        el: $('.spending'),
        initialize: function (context) {
            console.log(context);
            _.bindAll(this, 'render');
            this.render(context);
        },
        render: function (context) {
            var spend = new SpendingModel;

            spend.fetch({
                success: function (spend) {
                    console.log("fetch spending model success");
                    var template = _.template(spendingTemplate, {spending: spend});
                    this.$('.spending').html(template);
                },
                data: $.param({user: 'tom', key: context['key'], patients: context['id']})
            });


        }
    });
    return Spending;
});
//Chart codes are in the template file spending.html