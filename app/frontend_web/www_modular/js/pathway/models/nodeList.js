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
                _.each(childSet, function(cur){
                    var toAdd = new NodeModel(cur, curTree)
                    this.add(toAdd, {silent: true})
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

    return NodeList

});
