/**
 * Created by Asmaa Aljuhani on 3/14/14.
 */

define([
  'jquery',
  'underscore',
  'backbone',
  'models/orderModel'
], function($, _, Backbone, OrderModel){
  var OrderCollection = Backbone.Collection.extend({
        url: '/orders',
      model: OrderModel,

    initialize: function(){}

  });

  return OrderCollection;
});