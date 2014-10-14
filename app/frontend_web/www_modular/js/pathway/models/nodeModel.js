define([
    'jquery',
    'underscore',
    'backbone',
    'globalmodels/contextModel',

], function($, _, Backbone, contextModel){



   var NodeList = Backbone.Collection.extend({
        populate: function(childSet, curTree){
            if (childSet){
                for (var i in childSet){
                    var cur = childSet[i]
                    var toAdd = new NodeModel(cur, curTree)
                    toAdd.set('hasLeft', i!=0)
                    toAdd.set('hasRight', i<childSet.length-1)
                    this.add(toAdd, {silent: true})
                }
            }
        },
        toJSON: function(){

            var jsonList = []
            _.each(this.models, function(cur){
                jsonList.push(cur.toJSON())

            }, this)
            return jsonList
        }


    })

    var NodeModel = Backbone.Model.extend({
        defaults: {hideChildren: "false"},
        getNodeType: function(){

          return "treeNode"
        },

        initialize: function(params, curTree){
            if (!params.nodeID){
                this.set('nodeID', curTree.getNextNodeID(), {silent: true})
            } else {
                this.set('nodeID', params.nodeID, {silent: true})
            }
            if (!params.children){params.children = []}
            var newChildren = new NodeList()
            newChildren.populate(params.children, curTree)
            this.set({children: newChildren}, {silent:true})

            _.each(this.get('children').models, function(cur){
                cur.set({'hideChildren': "true"}, {silent: true})
            })
            this.set('hideChildren', "true", {silent: true})
            this.set('name', params.name, {silent: true})
            this.set('tooltip', params.tooltip, {silent: true})
            this.set('sidePanelText', params.sidePanelText, {silent: true})
            if (params.protocol){
                this.set('protocol', new Backbone.Model(params.protocol), {silent:true})
            }
        },
        toJSON: function(){
            var retMap = _.omit(this.attributes, ['children', 'hideChildren'])
            retMap.children = this.get('children').toJSON()
            return retMap
        }


    })
    return NodeModel

});
