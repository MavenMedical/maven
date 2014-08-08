define([
    'jquery',
    'underscore',
    'backbone',
    'models/contextModel',
    'models/nodeModel'

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

    return NodeList

});
