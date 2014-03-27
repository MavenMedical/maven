/**
 * Created by Asmaa Aljuhani on 3/14/14.
 */

define([
  'jquery',
  'underscore',
  'backbone',
  'currentContext',
  'models/orderModel'
], function($, _, Backbone, currentContext, OrderModel){
  var OrderCollection = Backbone.Collection.extend({
        url: '/orders',
      model: OrderModel,
      initialize: function(){
          console.log('order collection');
      }

    /*parse: function(response){
        console.log("parse");
        return this.model = response[currentContext.patients];
    }*/

  });

  return OrderCollection;
});