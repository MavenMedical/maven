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

    'text!templates/widget/orderable.html'
], function ($, _, Backbone, currentContext, orderRow, OrderModel, OrderCollection, orderableTemplate) {

    var Orderable = Backbone.View.extend({
        el: '.orderable',
        template: _.template(orderableTemplate),

        initialize: function () {
            console.log("ini orderable");
            _.bindAll(this, 'render', 'addOrder');
            this.orders = new OrderCollection();
            this.orders.bind('add', this.addOrder , this);
            this.orders.fetch({data:$.param(currentContext)});
            this.render();
        },
        render: function () {
            console.log("render orderables");
            this.$el.html(this.template);
        },
        addOrder: function(ord){
            console.log(ord);
            var orderrow = new orderRow({
              model: ord
            });
           //console.log(orderrow.render().el);
            $('#accordion').append(orderrow.render().el);
        }
    });
    return Orderable;
});
