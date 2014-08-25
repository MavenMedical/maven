define([
    'jquery',
    'underscore',
    'backbone',
   'globalmodels/contextModel',
    'pathway/models/nodeModel'

], function($, _, Backbone, contextModel, NodeModel){



    var NodeList = Backbone.Collection.extend({
        initialize: function(childSet){
            if (childSet){
                _.each(childSet, function(cur){
                    this.add(new NodeModel(cur), {silent: true})
                }, this)
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

        initialize: function(params){
            this.set({text: params.text + " NODE"},{silent:true})
            if (!params.children2){params.children2 = []}
            this.set({children: new NodeList(params.children2)}, {silent:true})
            this.set('name', params.name)
            this.set({protocol: params.protocol}, {silent:true})
            this.set({hideChildren: "false"}, {silent: true})


        },
        deleteNode: function(toDelete){
            var that = this
            _.each(this.get('children').models, function(cur){
                if (cur == toDelete){
                    that.get('children').remove(toDelete)
                } else {
                    cur.deleteNode(toDelete)
                }
            })



        },
        toJSON: function(){
            var retMap = _.omit(this.attributes, ['children', 'hideChildren'])
            retMap.children2 = this.get('children').toJSON()
            return retMap
        }


    })
    return NodeModel

});
