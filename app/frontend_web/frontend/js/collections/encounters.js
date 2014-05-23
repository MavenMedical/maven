/**
 * Created by Asmaa Aljuhani on 3/14/14.
 */

define([
  'jquery',
  'underscore',
  'backbone',
  'models/encounterModel'
], function($, _, Backbone, EncounterModel){
  var EncounterCollection = Backbone.Collection.extend({
    model: EncounterModel,

    initialize: function(){}

  });

  return EncounterCollection;
});