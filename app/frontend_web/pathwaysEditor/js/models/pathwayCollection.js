define([
    'jquery',
    'underscore',
    'backbone',
    'models/contextModel',
], function($, _, Backbone, contextModel){


    var pathCollection = Backbone.Collection.extend({
        elPairs: [],

        url: function() {

            return '/list?' + decodeURIComponent($.param(contextModel.toParams()));
        },
        initialize: function(){
            var that = this
            contextModel.on('change:auth', function(){
                that.fetch()

            })

        }



    })
    pathCollection = new pathCollection()
    return pathCollection

});
