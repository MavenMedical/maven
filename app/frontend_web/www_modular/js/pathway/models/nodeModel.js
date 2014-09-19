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

            if (!params.children){params.children = []}
            this.set({children: new NodeList(params.children)}, {silent:true})

            _.each(this.get('children').models, function(cur){
                cur.set({'hideChildren': "false"}, {silent: true})
            })
            this.set('hideChildren', "false", {silent: true})
            this.set('name', params.name, {silent: true})
            this.set('tooltip', params.tooltip, {silent: true})
            this.set('sidePanelText', params.sidePanelText, {silent: true})
            this.set('protocol', params.protocol, {silent:true})
        },
        toJSON: function(){
            var retMap = _.omit(this.attributes, ['children', 'hideChildren'])
            retMap.children = this.get('children').toJSON()
            return retMap
        }


    })
    return NodeModel

});
