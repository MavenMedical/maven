/**
 * Created by Asmaa Aljuhani on 3/17/14.
 * Resource collection is a collection of multiple Model subclasses
 *
 * Assumption: a universal URL to get all type of model
 */
define([
  'jquery',
  'underscore',
  'backbone',
  // List of subclass Model
], function($, _, Backbone){
  var ResourceCollection = Backbone.Collection.extend({

      url: '/resource',
/*
      parse: (resp, xhr) ->
    _(resp).map (attrs) ->
      switch attrs.type
        when 'UML' then new UmlLogbook attrs
        when 'Plane' then new PLaneLogbook attrs

class Logbooks extends Backbone.Collection

  model: (attrs, options) ->
    switch attrs.type
      when 'UML' then new UmlLogbook attrs, options
      when 'Plane' then new PLaneLogbook attrs, options
      # should probably add an 'else' here so there's a default if,
      # say, no attrs are provided to a Logbooks.create call

  url: 'api/logbooks'
  */





    initialize: function(){
        console.log("collection");
          }

  });

  return PatientCollection;
});
