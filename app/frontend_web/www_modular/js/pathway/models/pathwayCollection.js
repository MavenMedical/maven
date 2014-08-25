define([
    'jquery',
    'underscore',
    'backbone',
   'globalmodels/contextModel',
    'globalmodels/contextModel'
], function($, _, Backbone, c, contextModel){


    var pathCollection = Backbone.Collection.extend({
        elPairs: [],

        url: function() {

            return '/list?' + decodeURIComponent($.param(contextModel.toParams()));
        },
        initialize: function(){
            this.fetch()

        }



    })
    pathCollection = new pathCollection()
    return pathCollection

});
