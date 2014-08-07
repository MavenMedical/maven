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


           this.set({text: response.text}, {silent: true})
           this.set({id: response.id}, {silent: true})
           this.set({protocol: response.protocol}, {silent: true})
            this.set({children: new NodeList(response.children)}, {silent: true})
            _.each(this.get('children').models, function(cur){
                cur.set({'hideChildren': true}, {silent: true})
            })
           this.set({triggers: new Backbone.Collection(response.triggers)}, {silent: true})
        }

    })
    treeModel = new TreeModel()
    return treeModel

});
