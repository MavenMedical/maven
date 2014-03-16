/**
 * Created by Asmaa Aljuhani on 3/14/14.
 */

define([
  'jquery',
  'underscore',
  'backbone',
  'models/patientModel'
], function($, _, Backbone, PatientModel){
  var PatientCollection = Backbone.Collection.extend({

      url: '/patients',
    model: PatientModel,

    initialize: function(){
        console.log("collection");
          }

  });

  return PatientCollection;
});