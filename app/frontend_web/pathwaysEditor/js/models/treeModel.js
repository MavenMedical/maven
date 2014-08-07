define([
    'jquery',
    'underscore',
    'backbone',
    'models/contextModel',
    'models/nodeList'
], function($, _, Backbone, contextModel, NodeList){
    var treeModel;


    var TreeModel = Backbone.Model.extend({
        elPairs: [],
        url: function() {

            return '/tree?' + decodeURIComponent($.param(contextModel.toParams()));
        },

        initialize: function(){
            this.set('triggers', new Backbone.Collection())
            this.set('text', "Triggers")
            this.set('children', new NodeList())
            this.elPairs = []
        },
        toJSON: function(){
            return this.attributes


        },
        parse: function(response){
           this.set('text', response.text)
           this.set('id', response.id)
           this.set('protocol', response.protocol)
           this.set('children', new NodeList(response.children))
           this.set('triggers', new Backbone.Collection(response.triggers))
        }

    })
    treeModel = new TreeModel()
    return treeModel

});
