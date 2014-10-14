define([
    'jquery',
    'underscore',
    'backbone',
   'globalmodels/contextModel',
    'pathway/models/nodeModel'

], function($, _, Backbone, contextModel, NodeModel){

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

    return NodeList

});
