define([
    'jquery',
    'underscore',
    'backbone',
    'globalmodels/contextModel',
    'pathway/models/nodeModel',
    'pathway/models/pathwayCollection',
    'pathway/models/treeContext',
    'pathway/models/triggerGroupCollection'
], function ($, _, Backbone, contextModel, nodeModel, pathwayCollection, treeContext, triggerGroupCollection) {
    var CURRENT_VERSION = "version1";
    var treeModel;
    //delete a node and either delete its children, or move them to its parent node
    var deleteRecur = function (me, toDelete, saveChildren) {
        if (!me.get('isProtocol')) {
            for (var i in me.get('children').models) {
                var cur = me.get('children').models[i]
                if (cur == toDelete) {
                    var startLoc = me.get('children').indexOf(cur)
                    if (saveChildren) {
                        var savedChildren = cur.get('children').models
                        for (var i in savedChildren) {
                            var cur2 = savedChildren[i]
                            if (me.get('children').length == 1 || !cur2.get('isProtocol')) {
                                me.get('children').add(cur2, {at: startLoc, silent: true})
                                startLoc = startLoc + 1
                            }
                        }
                    }


                    me.get('children').remove(toDelete, {silent: true})
                } else {
                    deleteRecur(cur, toDelete, saveChildren)
                }
            }
        }

    }

    //find the node with the given id
    var getNodeByID = function(head, target){
        var toCheck = [head]
        while (toCheck){
            var cur = toCheck.pop()
            if (cur.get('nodeID') == target){
                return cur
            }
            toCheck = toCheck.concat(cur.get('children').models)
        }

    }
    //alter the child visiblity in order to show a path to the target node
    var openPathToTarget = function (cur, target, path) {

        if (cur.get('nodeID') == target) {
            for (var i in path) {
                var cur2 = path[i]
                cur2.showChildren && cur2.showChildren()
            }
            return cur
        } else {
            var list = []
            if (!cur.get('isProtocol')) {
                for (var i in cur.get('children').models) {
                    var cur2 = cur.get('children').models[i]
                    var temp = path.slice(0)
                    temp.push(cur2)
                    var n = openPathToTarget(cur2, target, temp)
                    if (n) return n
                }
            }
        }
    }
    //move a node relative to its siblings under its parent
    var nodePosition = function (cur, target, change, pointer) {

        var doWork = false
        var siblingSet = []
        if (cur.get('isProtocol')) return
        for (var i in cur.get('children').models) {
            var cur2 = cur.get('children').models[i]
            siblingSet[siblingSet.length] = cur2
            if (doWork == false && cur2 != target) {
                nodePosition(cur2, target, change, pointer)
            } else {
                doWork = true
            }
        }
        var last
        if (doWork) {

            for (var key in siblingSet) {
                key = parseInt(key)
                var val = siblingSet[key]
                if (val == target) {
                    if (change == -1) {
                        siblingSet[key] = last
                        siblingSet[key - 1] = val

                        siblingSet[key].set('hasRight', key < (siblingSet.length - 1), {silent: true})
                        siblingSet[key - 1].set('hasLeft', (key - 1) != 0, {silent: true})
                        siblingSet[key - 1].set('hasRight', true, {silent: true})
                        siblingSet[key].set('hasLeft', true, {silent: true})
                        break;

                    } else if (change == 1) {
                        siblingSet[key] = siblingSet[key + 1]
                        siblingSet[key + 1] = val

                        siblingSet[key + 1].set('hasRight', (key + 1) < (siblingSet.length - 1), {silent: true})
                        siblingSet[key].set('hasLeft', key != 0, {silent: true})
                        siblingSet[key].set('hasRight', true, {silent: true})
                        siblingSet[key + 1].set('hasLeft', true, {silent: true})
                        break;
                    }
                }
                last = val
            }
            pointer.parent = cur
            pointer.child = siblingSet

        }

    }

    var findCurNode = function (me) {

        if (!me.get('isProtocol')) {
            var toCheck = []
            for (var x in me.get('children').models) {
                var cur = me.get('children').models[x]
                if (cur.childrenHidden && !cur.childrenHidden()) {
                    toCheck.push(cur)

                }
            }
            var ret = []
            if (toCheck.length == 0) {
                ret.push(me.get('nodeID'))
            }

            for (x in toCheck) {
                var cur = toCheck[x]
                ret = ret.concat(findCurNode(cur))
            }
            return ret


        } else {
            return ([me.get('nodeID')])
        }
    }
    //find the parent of the chosen node and collape all of its children other than the target
    var hideSiblingsRecur = function (me, toHide) {

        if (me.get('isProtocol')) return


        //var tar = _.indexOf(me.get('children').models, toHide)
        var tar = _.indexOf(me.get('children').models, toHide)
        for (var i in me.get('children').models) {
            if (tar != -1) {
                if (i != tar) {
                    recursiveCollapse(me.get('children').models[i])
                }
            }
            else {
                hideSiblingsRecur(me.get('children').models[i], toHide)
            }
        }
    }
    //collapse the entire tree
    var recursiveCollapse = function (node) {


        if (node.get('isProtocol')) return
        node.hideChildren()
        _.each(node.attributes.children.models, function (cur) {
            recursiveCollapse(cur)
        })

    }
    //expand the entire tree
    var recursiveExpand = function (node) {
        if (node.get('isProtocol')) return
        node.showChildren()
        _.each(node.attributes.children.models, function (cur) {
            recursiveCollapse(cur)
        })

    }

    //Model for a currently loaded pathway
    var TreeModel = nodeModel.extend({
        elPairs: [],
	    idAttribute: 'pathid',
        urlRoot: '/tree',
        //call the recursion to move this node relative to its siblings
        changeNodePosition: function (target, change) {
            var pointer = {}
            var r = nodePosition(this, target, change, pointer)
            var parent = pointer.parent
            var children = pointer.child
            parent.set('children', new Backbone.Collection(children), {silent: true})
            this.trigger('propagate')
        },
        //call the recursion to expand the entire tree
        expandAll: function () {
            recursiveExpand(this)
        },
        //find the code representing a path expanded to the current tree state
        getShareCode: function () {
            var nodes = findCurNode(this)
            var nodestr = ""
            for (var i in nodes) {
                var cur = nodes[i]
                nodestr += "-" + cur
            }
            if (contextModel.get('page') == "pathEditor") {
                Backbone.history.navigate("pathwayeditor/" + contextModel.get('pathid') + "/node/" + nodestr);
            } else {
                Backbone.history.navigate("pathway/" + contextModel.get('pathid') + "/node/" + nodestr);
            }
            contextModel.set('code', nodestr)

        },
        //call the recursion to find the node object in the tree with the given id
        getNodeByID: function(target){
            return getNodeByID(this, target)
        },

        //expand a path to each of the following id's and update the url to the representative string
        getPathToIDS: function (ids) {
            this.collapse(this)
            if (!ids && contextModel.get('code')) {
                ids = _.filter(contextModel.get('code').split('-'), _.identity)
            }
            for (var i in ids) {
                var cur = ids[i]
                if (cur) {
                    var node = openPathToTarget(this, (cur), [this])
                    if (node && ids.length==1 && !treeContext.get('selectedNode')) {
                        treeContext.set('selectedNode', node, {silent: true});
                    }
                }
            }
        },
        initialize: function () {
            //this.on('all', function(evt) {
            //console.log(evt)}
            //)
            this.set({
                'triggers': new Backbone.Collection(),
                'tooltip': 'triggers tooltip',
                'sidePanelText': "",
                'name': "Triggers"
            })
            this.populateChildren();
            var that = this
            //if the page changes, redraw
            contextModel.on('change:page', function () {
                treeContext.trigger('propagate')
            })
            //if the pathid changes load the new pathway
            contextModel.on('change:pathid', function () {
                var newpathid = contextModel.get('pathid')
                if (newpathid && newpathid != '0') {
                    treeContext.clear()

                    that.getPathToIDS()


                    var oldpathid = that.get('pathid')
                    that.set({pathid: newpathid}, {silent: true})
                    if (newpathid != oldpathid) {
                        that.fetch()
                    }
                }
                if (contextModel.get('page') == 'pathEditor') {
                    require(['ckeditor'], function () {
                    })
                    Backbone.history.navigate("pathwayeditor/" + newpathid + "/node/" + contextModel.get('code'));
                } else {
                    var code = contextModel.get('code')
                    Backbone.history.navigate("pathway/" + newpathid + "/node/" + code);
                }
            })
            //if the code representing the currently expanded path changes change the expansion state to the new one
            contextModel.on('change:code', function () {
                if (contextModel.get('code')) {
                    that.getPathToIDS()
                    treeContext.trigger('propagate')
                }
            })
            //if anything calls propogate on this model, it is indicating that it needs an update to persistance
            //call a save and rerender
            this.on('propagate', function () {
                if (this.oldContent != JSON.stringify(this.toJSON())) {
                    this.save(null, {
                        error: function () {
                            alert("Auto Save failed")

                        }
                    })
                } else {
                    treeContext.trigger('propagate')
                }
            }, this)
            this.on('sync', function (obj, data) {
                this.oldContent = JSON.stringify(this.toJSON())
                this.set({'pathid': data.pathid}, {silent: true})
                contextModel.set({'pathid': String(data.pathid), 'canonical': String(data.canonical)})
                pathwayCollection.fetch()
                if (contextModel.get('code')) {
                    that.getPathToIDS()
                } else {
                    if (contextModel.get('page') == "pathEditor") {
                        that.expandAll()
                    } else {
                        that.collapse()
                    }
                }

                treeContext.trigger('propagate')
            }, this)
            if (contextModel.get('pathid')) {
                that.set({pathid: contextModel.get('pathid')}, {silent: true})
                this.getPathToIDS()
                this.fetch()
                treeContext.trigger('propagate')
            }
            if (contextModel.get('page') == 'pathEditor') {
                require(['ckeditor'], function () {
                })
            }
            this.elPairs = []
        },
        //find the next node id to assign to a newly created node
        getNextNodeID: function () {
            this.set('nodeCount', this.get('nodeCount') + 1, {silent: true})
            return this.get('nodeCount')
        },
        //call the recursion to hide all the siblings of the chosen node
        hideSiblings: function (toHide) {
            hideSiblingsRecur(this, toHide)
        },
        //call the recursion to collapse the entire tree, or all of the children of a given node
        collapse: function (node) {
            if (!node) {
                recursiveCollapse(this)
            } else {
                recursiveCollapse(node)
            }
        },
        //call the recursion to delete a given node and either delete its children, or move them up
        deleteNode: function (toDelete, saveChildren) {

            deleteRecur(this, toDelete, saveChildren)
            this.save()
        },
        //string representing that this is the model of a top level tree
        getNodeType: function () {
            return "treeModel"
        },
        //convert this tree to a persistance friendly json
        toJSON: function (options) {
            if (!options) {
                options = {}
            }
            var retMap = _.omit(this.attributes, ['children', 'triggers', 'hasLeft', 'hasRight'])
            if (options && options.toExport) {
                retMap = _.omit(retMap, ['nodeID', 'nodeCount', 'id', 'pathid'])
            }
            retMap.children = this.get('children').toJSON(options)
            retMap.triggers = this.get('triggers').toJSON()

            /*     retMap.triggers = retMap.triggers.toJSON()
             for (var i in retMap.triggers){

             var curGroup = retMap.triggers[i]
             curGroup['details'] = curGroup['details'].toJSON()
             var curDetailsModel = curGroup['details']

             for (var i2 in curDetailsModel){
             curDetailsModel[i2] = curDetailsModel[i2].toJSON()

             }
             }
             */
            //console.log('the json will look like', retMap)

            return retMap
        },

        //create a new pathway with the given name and load it
        loadNewPathway: function (params, options) {

            this.set({
                'triggers': new Backbone.Model(),
                'sidePanelText': "",
                'tooltip': params.tooltip,
                'name': params.name,
                'protocol': null,
                'nodeCount': 0,
                'nodeID': 0, 
                'folder': params.folder
            }, {silent: true})
            this.populateChildren()
           var n = new triggerGroupCollection()
            n.populate()
            this.set('triggers', n, {silent: true});
            this.unset('pathid', {silent: true})
            var that = this

            //once the correct data is modeled in the pathway, save it and get the id back
            this.save({}, {
                success: function (ogj, data) {
                    pathwayCollection.fetch()
                    params.pathid = data.pathid
                    if (options && options.toImport) {
                        that.parse(params, options)
                        that.save({},
                            {
                                success: function () {
                                    contextModel.set({'pathid': that.get('pathid')})
                                    Backbone.history.navigate("pathwayeditor/" + that.get('pathid') + "/node/undefined");
                                    pathwayCollection.fetch()
                                }
                            })

                    } else {
                        contextModel.set({'pathid': data.pathid})
                        Backbone.history.navigate("pathwayeditor/" + that.get('pathid') + "/node/undefined");
                        pathwayCollection.fetch()
                    }
                }
            })

        },
        //when this model fetches a json from persistance, this indicates how to parse it into the model
        parse: function (response, options) {

            //if the protocol doesnt have a version tag it as a preversion protocol, otherwise tag it with its given version
            if (!response.protocolVersion) {
                this.set('protocolVersion', "preversion", {silent: true})
            } else {
                this.set('protocolVersion', response.protocolVersion, {silent: true})
            }
            var self = this;

           //different parse functions based on the version of the protocol we want
            var versions = {
                "preversion": function (response, options) {
                    if (options && options.toImport) {
                        response = _.omit(response, ['nodeID', 'nodeCount'])
                    }
                    if (!response.nodeCount) {
                        self.set({nodeCount: 0}, {silent: true})
                    } else {
                        self.set('nodeCount', response.nodeCount, {silent: true})
                    }
                    if (!response.nodeID) {
                        self.set('nodeID', self.getNextNodeID(), {silent: true})
                    } else {
                        self.set('nodeID', response.nodeID, {silent: true})
                    }
                    self.set({
                        tooltip: response.tooltip,
                        sidePanelText: response.sidePanelText,
                        pathid: response.pathid,
                        protocol: response.protocol,
                        name: response.name
                    }, {silent: true})
                    self.populateChildren(response.children, options)
                    var n = new triggerGroupCollection()
                    n.populate(response.triggers, self.get('protocolVersion'));
                    self.set('triggers', n, {silent: true});
                },
                "version1": function (response, options) {
                    if (options && options.toImport) {
                        response = _.omit(response, ['nodeID', 'nodeCount'])
                    }
                    if (!response.nodeCount) {
                        self.set({nodeCount: 0}, {silent: true})
                    } else {
                        self.set('nodeCount', response.nodeCount, {silent: true})
                    }
                    if (!response.nodeID) {
                        self.set('nodeID', self.getNextNodeID(), {silent: true})
                    } else {
                        self.set('nodeID', response.nodeID, {silent: true})
                    }
                    self.set({
                        tooltip: response.tooltip,
                        sidePanelText: response.sidePanelText,
                        pathid: response.pathid,
                        protocol: response.protocol,
                        name: response.name
                    }, {silent: true})
                    self.populateChildren(response.children, options)
                    var n = new triggerGroupCollection()
                    n.on('cascade', function () {
                        self.save(null, {
                            error: function () {
                                alert("Autosave Failed")
                            }
                        })

                    })

                    n.populate(response.triggers, self.get('protocolVersion'));

                    self.set('triggers', n, {silent: true});
                }

            }
            //call the correct parse function
            versions[this.get('protocolVersion')](response, options)
            //upon parse completion the model matches the current version so update it
            this.set('protocolVersion', CURRENT_VERSION)
        }
    });

    treeModel = new TreeModel()
    return treeModel

});
