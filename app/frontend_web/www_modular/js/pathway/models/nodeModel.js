define([
    'jquery',
    'underscore',
    'backbone',
    'globalmodels/contextModel',
    'pathway/models/treeContext',
    'pathway/models/triggerGroupCollection'
], function ($, _, Backbone, contextModel, treeContext, triggerGroupCollection) {

    var NodeModel;
    var NodeList = Backbone.Collection.extend({
        populate: function (childSet, curTree, options) {
            if (childSet) {
                for (var i in childSet) {
                    var cur = childSet[i]
                    var toAdd
                    if (cur.children) {
                        toAdd = new NodeModel(cur, curTree, options)
                        toAdd.set('hasLeft', i != 0)
                        toAdd.set('hasRight', i < childSet.length - 1)
                    } else {
                        toAdd = new Backbone.Model(cur)
                        toAdd.set('isProtocol', true) //if this is an old protocol without a isProtocol add it
                    }

                    this.add(toAdd, {silent: true})
                }
            }
        },
        toJSON: function (options) {

            var jsonList = []
            _.each(this.models, function (cur) {
                jsonList.push(cur.toJSON(options))

            }, this)
            return jsonList
        }
    })

    NodeModel = Backbone.Model.extend({
        getNodeType: function () {

            return "treeNode"
        },

        initialize: function (params, curTree, options) {

            if (!params.nodeID) {
                this.set('nodeID', curTree.get('pathid') + ":" + curTree.getNextNodeID(), {silent: true})
            } else {
                this.set('nodeID', params.nodeID, {silent: true})
            }
            if (!params.children) {
                params.children = []
            }
         //create the children representation if needed
            var newChildren = new NodeList()
            newChildren.populate(params.children, curTree, options)

         //Create the trigger representation if needed
             var myTriggerModel = new triggerGroupCollection()
             if (params.triggers){
                myTriggerModel.populate(params.triggers, curTree.get('protocolVersion'))
             } else {
                myTriggerModel.populate()
             }
                myTriggerModel.on('cascade', function () {
                    curTree.trigger('propagate')
                })


            this.set({
                triggers: myTriggerModel,
                children: newChildren,
                'name': params.name,
                'tooltip': params.tooltip,
                'sidePanelText': params.sidePanelText
            }, {silent: true})
            this.hideChildren()
            _.each(this.get('children').models, function (cur) {
                if (cur.showChildren) {
                    cur.showChildren()
                }
            })
            if (params.protocol) {
                if (!params.protocol.nodeID) {
                    params.protocol.nodeID = curTree.getNextNodeID()
                }
                this.get('children').add(new Backbone.Model(params.protocol))
            }

        },
        toJSON: function (options) {
            var retMap = _.omit(this.attributes, ['children', 'hasLeft', 'hasRight', 'triggers'])
            if (options.toExport) {
                retMap = _.omit(retMap, ['nodeID'])
            }
            if (this.get('triggers')){
                retMap.triggers = this.get('triggers').toJSON()
            }
            retMap.children = this.get('children').toJSON(options)
            return retMap
        },
        populateChildren: function (children, options) {
            var newChildren = new NodeList()
            if (children) {
                newChildren.populate(children, this, options)
            }
            this.set({children: newChildren}, {silent: true})
        },
        populateTriggers: function (triggerJSON, curTree) {


         },


    showChildren: function () {
        treeContext.unset(this.get('nodeID'))
    }
    ,
    hideChildren: function () {
        treeContext.set(this.get('nodeID'), 'hideChildren')
    }
    ,
    childrenHidden: function () {
        return treeContext.get(this.get('nodeID'))
    }


})
return NodeModel

})
;
