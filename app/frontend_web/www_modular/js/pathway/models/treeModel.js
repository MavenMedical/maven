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
    var hideSiblingsRecur = function(me, toHide){
        var flag = false;
        var tar = me.get('children').models.indexOf(toHide)
                        console.log("the parent is", me, "tar is", tar)
                        console.log("to delete is", toHide)
        for (var i in me.get('children').models){
                if (tar != - 1){
                     if (i != tar){
                        console.log(me.get('children').models[i])
                        me.get('children').models[i].set('hideChildren', "true")
                     }
                     flag = true;
                }
                else {
                    hideSiblingsRecur(me.get('children').models[i], toHide)
                }
        }
    }
    var TreeModel = Backbone.Model.extend({
        elPairs: [],
        url: function() {

            return '/tree?' + decodeURIComponent($.param(contextModel.toParams()));
        },

        initialize: function(){

            console.log('init treeModel',contextModel.get('pathid') );

            this.set('triggers', new Backbone.Collection())
            this.set('tooltip', 'triggers tooltip')
            this.set('children', new NodeList())
            this.set('sidePanelText', "")
            this.set('name', "Triggers")
            var that = this
            contextModel.on('change:pathid', function(){
                that.fetch()
                Backbone.history.navigate("pathway/1/pathid/"+contextModel.get('pathid'));
            })
            this.fetch();
            this.elPairs = []


        },
        hideSiblings: function(toHide){
            hideSiblingsRecur(this, toHide)
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
        getNodeType: function(){
          return "treeModel"
        },
        toJSON: function(){
            var retMap = _.omit(this.attributes, ['children', 'hideChildren', 'selectedNode'])
            retMap.children = this.get('children').toJSON()
            return retMap
        },
        loadNewPathway: function(params){
            this.set('triggers', new Backbone.Collection(), {silent: true})
            this.set('sidePanelText', "",  {silent: true})
            this.set('tooltip', params.tooltip, {silent: true})
            this.set('children', new NodeList(), {silent: true})
            this.set('name', params.name, {silent: true})
            this.set('protocol', null, {silent: true})
            this.unset('id', {silent: true})
            var that = this
            this.save({}, {success: function(){
                    pathwayCollection.fetch()
                }
            })
        },
        parse: function(response){
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
