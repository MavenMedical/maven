define([
    'jquery',
    'underscore',
    'backbone',
    'globalmodels/contextModel',

], function($, _, Backbone, contextModel){

    var NodeModel;
    var NodeList = Backbone.Collection.extend({
        populate: function(childSet, curTree, options){
            if (childSet){
                for (var i in childSet){
                    var cur = childSet[i]
                    var toAdd
                    if (cur.children){
                        toAdd = new NodeModel(cur, curTree, options)
                        toAdd.set('hasLeft', i!=0)
                        toAdd.set('hasRight', i<childSet.length-1)
                    } else  {
                        toAdd = new Backbone.Model(cur)
                        toAdd.set('isProtocol', true) //if this is an old protocol without a isProtocol add it
                     }

                        if (!toAdd.nodeID){
                            toAdd.set('nodeID', curTree.get('id') + ":" + curTree.getNextNodeID())
                        }
                    this.add(toAdd, {silent: true})
                }
            }
        },
        toJSON: function(options){

            var jsonList = []
            _.each(this.models, function(cur){
                jsonList.push(cur.toJSON(options))

            }, this)
            return jsonList
        }
    })

    NodeModel = Backbone.Model.extend({
        defaults: {hideChildren: "false"},
        getNodeType: function(){

          return "treeNode"
        },

        initialize: function(params, curTree, options){

            if (!params.nodeID){
                this.set('nodeID', curTree.get('id') + ":" + curTree.getNextNodeID(), {silent: true})
            } else {
                this.set('nodeID', params.nodeID, {silent: true})
            }
            if (!params.children){params.children = []}
            var newChildren = new NodeList()
            newChildren.populate(params.children, curTree, options)
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
		if (!params.protocol.nodeID) {
		    params.protocol.nodeID = curTree.getNextNodeID()
		}
                this.get('children').add(new Backbone.Model(params.protocol) )
            }
        },
        toJSON: function(options){
            var retMap = _.omit(this.attributes, ['children', 'hideChildren', 'hasLeft', 'hasRight'])
	    if (options.toExport) {retMap = _.omit(retMap, ['nodeID'])}
            retMap.children = this.get('children').toJSON(options)
            return retMap
        },
	populateChildren: function(children, options) {
            var newChildren = new NodeList()
	    if (children) {
		newChildren.populate(children, this, options)
	    }
	    this.set({children: newChildren}, {silent: true})
	}


    })
    return NodeModel

});
