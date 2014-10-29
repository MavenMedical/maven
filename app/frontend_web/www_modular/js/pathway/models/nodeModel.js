define([
    'jquery',
    'underscore',
    'backbone',
    'globalmodels/contextModel',

], function($, _, Backbone, contextModel){

    var NodeModel;
    var NodeList = Backbone.Collection.extend({
        populate: function(childSet, curTree){
            if (childSet){
                for (var i in childSet){
                    var cur = childSet[i]
                    var toAdd
                    if (cur.children){
                        toAdd = new NodeModel(cur, curTree)
                        toAdd.set('hasLeft', i!=0)
                        toAdd.set('hasRight', i<childSet.length-1)
                    } else  {
                        toAdd = new Backbone.Model(cur)
			if (!toAdd.nodeID){ 
			    toAdd.nodeID = curTree.get('id') + ":" + curTree.getNextNodeID()
			}
                    }
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

    NodeModel = Backbone.Model.extend({
        defaults: {hideChildren: "false"},
        getNodeType: function(){

          return "treeNode"
        },

        initialize: function(params, curTree){

            if (!params.nodeID){
                this.set('nodeID', curTree.get('id') + ":" + curTree.getNextNodeID(), {silent: true})
            } else {
                this.set('nodeID', params.nodeID, {silent: true})
            }
            if (!params.children){params.children = []}
            var newChildren = new NodeList()
            newChildren.populate(params.children, curTree)
            this.set({
		children: newChildren,
		'hideChildren': "true",
		'name': params.name,
		'tooltip': params.tooltip,
		'sidePanelText': params.sidePanelText
	    }, {silent: true})
            _.each(this.get('children').models, function(cur){
                cur.set({'hideChildren': "false"}, {silent: true})
            })
            if (params.protocol){
                this.get('children').add(new Backbone.Model(params.protocol) )
            }
        },
        toJSON: function(){
            var retMap = _.omit(this.attributes, ['children', 'hideChildren'])
            retMap.children = this.get('children').toJSON()
            return retMap
        },
	populateChildren: function(children) {
            var newChildren = new NodeList()
	    if (children) {
		newChildren.populate(children, this)
	    }
	    this.set({children: newChildren}, {silent: true})
	}


    })
    return NodeModel

});
