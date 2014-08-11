define([
    'jquery',
    'underscore',
    'backbone',
    'models/contextModel',
], function($, _, Backbone, contextModel){
    var pathCollection;


    var TreeModel = Backbone.Collection.extend({
        elPairs: [],
        url: function() {

            return '/list?' + decodeURIComponent($.param(contextModel.toParams()));
        }



    })
    pathCollection = new TreeModel()
    return pathCollection

});
