define([
    'jquery',
    'underscore',
    'backbone',
    'globalmodels/contextModel'
], function($, _, Backbone, contextModel){


    var pathCollection = Backbone.Collection.extend({
        elPairs: [],

	model: Backbone.Model.extend({idAttribute: 'canonical'}),
        url: function() {

            return '/list'
        },
        initialize: function(){
            this.fetch()

        }



    })
    pathCollection = new pathCollection()
    return pathCollection

});
