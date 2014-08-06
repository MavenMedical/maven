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

        initialize: function(params){
            this.set({text: params.text + " NODE"},{silent:true})
            this.set({'children': new NodeList()},{silent:true})
            this.set({protocol: params.protocol}, {silent:true})
            if (params.children){
                this.set({children: new NodeList(params.children)}, {silent:true})

            }
        },
        toJSON: function(){
            return this.attributes

        }


    })
    return NodeModel

});
