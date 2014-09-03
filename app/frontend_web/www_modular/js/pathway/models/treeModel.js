define([
    'jquery',
    'underscore',
    'backbone',
    'globalmodels/contextModel',
    'pathway/models/nodeList',
    'pathway/models/pathwayCollection'
], function($, _, Backbone, contextModel, NodeList, pathwayCollection){
    var treeModel;

    var deleteRecur = function(me , toDelete){
            _.each(me.get('children').models, function(cur){
                if (cur == toDelete){
                    me.get('children').remove(toDelete)
                } else {
                    deleteRecur(cur, toDelete)
                }
        })
    }

    var TreeModel = Backbone.Model.extend({
        elPairs: [],
        url: function() {

            return '/tree?' + decodeURIComponent($.param(contextModel.toParams()));
        },

        initialize: function(){

            this.set('triggers', new Backbone.Collection())
            this.set('tooltip', 'triggers tooltip')
            this.set('children', new NodeList())
            this.set('name', "Triggers")
            var that = this
            contextModel.on('change:pathid', function(){
                that.fetch()
                Backbone.history.navigate("pathway/1/pathid/"+contextModel.get('pathid'));
            })

            this.elPairs = []


        },

        deleteNode: function(toDelete){
            var that = this
                _.each(this.get('children').models, function(cur){
                    if (cur == toDelete){
                      that.get('children').remove(toDelete)
                    } else {
                       deleteRecur(cur, toDelete)
                    }
                })
            this.trigger('propagate')
        },
        getType: function(){
          return "treeModel"
        },
        toJSON: function(){
            var retMap = _.omit(this.attributes, ['children', 'hideChildren'])
            retMap.children = this.get('children').toJSON()
            return retMap
        },
        loadNewPathway: function(params){
            console.log('params', params)
            this.set('triggers', new Backbone.Collection(), {silent: true})
            this.set('sidePanelText', params.sidePanelText,  {silent: true})
            this.set('tooltip', params.tooltip, {silent: true})
            this.set('children', new NodeList(), {silent: true})
            this.set('name', params.name, {silent: true})
            this.unset('protocol', {silent: true})
            this.unset('id', {silent: true})
            var that = this
            this.save({}, {success: function(){
                    pathwayCollection.fetch()
                }
            })
        },
        parse: function(response){
            console.log(response)
            this.set({tooltip: response.tooltip}, {silent: true})
            this.set({sidePanelText: response.sidePanelText}, {silent: true})
            this.set({id: response.pathid}, {silent: true})
            this.set({protocol: response.protocol}, {silent: true})
            this.set({name: response.name}, {silent: true})
            this.set({children: new NodeList(response.children)}, {silent: true})
            this.set({hideChildren: false}, {silent: true})
            _.each(this.get('children').models, function(cur){
                cur.set({'hideChildren': "false"}, {silent: true})
            })
           this.set({triggers: new Backbone.Collection(response.triggers)}, {silent: true})

        }

    })
    treeModel = new TreeModel()
    return treeModel

});
