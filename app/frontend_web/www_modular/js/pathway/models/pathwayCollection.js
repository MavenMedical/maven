define([
    'jquery',
    'underscore',
    'backbone',
    'globalmodels/contextModel'
], function($, _, Backbone, contextModel){


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
