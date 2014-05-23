/**
 * Created by Asmaa Aljuhani on 3/11/14.
 */

define([
    // These are path alias that we configured in our main.js
    'jquery',     // lib/jquery/jquery
    'underscore', // lib/underscore/underscore
    'backbone',    // lib/backbone/backbone

    'currentContext',

    //sub view
    '../singleRow/orderRow',

     //Model
    'models/orderModel',

    //Collection
    'collections/orders',

    'text!templates/templatesA/widget/orderable.html'
], function ($, _, Backbone, currentContext, orderRow, OrderModel, OrderCollection, orderableTemplate) {

    var Orderable = Backbone.View.extend({
        el: '.orderable',
        template: _.template(orderableTemplate),

        initialize: function () {
            this.render();
        },
        render: function () {
            this.$el.html(this.template);
             return this;
        },
        addOrder: function(ord){
            var orderrow = new orderRow({
              model: ord
            });
            $('#accordion').append(orderrow.render().el);
        }
    });
    return Orderable;
});
