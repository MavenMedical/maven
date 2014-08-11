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

            //if the new path button is clicked, create a new tree and save it

            this.elPairs = []
        },
        toJSON: function(){
            return this.attributes


        },
        loadNewPathway: function(params){
            this.set('triggers', new Backbone.Collection(), {silent: true})
            this.set('text', params.name, {silent: true})

            this.set('children', new NodeList(), {silent: true})
            this.set('name', params.name, {silent: true})
            this.unset('protocol', {silent: true})
            this.unset('id', {silent: true})

            this.save()


        },
        parse: function(response){
            console.log('parsing', response.id)
            this.set({text: response.text}, {silent: true})
            this.set({id: response.id}, {silent: true})
            this.set({protocol: response.protocol}, {silent: true})
            this.set({name: response.name}, {silent: true})
            this.set({children: new NodeList(response.children)}, {silent: true})
            _.each(this.get('children').models, function(cur){
                cur.set({'hideChildren': "true"}, {silent: true})
            })
           this.set({triggers: new Backbone.Collection(response.triggers)}, {silent: true})
        }

    })
    treeModel = new TreeModel()
    return treeModel

});
