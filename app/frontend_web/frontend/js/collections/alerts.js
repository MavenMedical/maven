/**
 * Created by Asmaa Aljuhani on 3/14/14.
 */

define([
  'jquery',
  'underscore',
  'backbone',
  'models/alertModel'
], function($, _, Backbone, AlertModel){
  var AlertCollection = Backbone.Collection.extend({
      url: '/alerts',
    model: AlertModel,

    initialize: function(){}

  });

  return AlertCollection;
});