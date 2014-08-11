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

    var NodeModel = Backbone.Model.extend({
        defaults: {hideChildren: "true"},
        initialize: function(params){
            this.set({text: params.text + " NODE"},{silent:true})
            if (!params.children){params.children = []}
            this.set({children: new NodeList(params.children)}, {silent:true})
            this.set('name', params.name)
            this.set({protocol: params.protocol}, {silent:true})
            this.set({hideChildren: "true"}, {silent: true})


        },
        toJSON: function(){
            return this.attributes

        }


    })
    return NodeModel

});
