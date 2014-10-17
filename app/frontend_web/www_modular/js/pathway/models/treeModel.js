define([
    'jquery',
    'underscore',
    'backbone',
    'globalmodels/contextModel',
    'pathway/models/nodeList',
    'pathway/models/pathwayCollection'
], function($, _, Backbone, contextModel, NodeList, pathwayCollection){
    var treeModel;

    var deleteRecur = function(me , toDelete, saveChildren){
            for (var i in me.get('children').models){
                var cur = me.get('children').models[i]
                if (cur == toDelete){
                    var startLoc = me.get('children').indexOf(cur)
                    if (saveChildren){
                       var savedChildren =  cur.get('children').models
                       for (var i in savedChildren){
                           var cur2 = savedChildren[i]
                           me.get('children').add(cur2, {at: startLoc, silent: true})
                           startLoc = startLoc+1
                       }
                    }


                    me.get('children').remove(toDelete, {silent: true})
                } else {
                    deleteRecur(cur, toDelete, saveChildren)
                }
        }
     }

    var openPathToTarget = function(cur, target, path){
        if (cur.get('nodeID') == target){
            for (var i in path){
                var cur2 = path[i]
                cur2.set('hideChildren', "false",  {silent: true})

            }

        } else {
            var list = []
            for (var i in cur.get('children').models){
                var cur2 = cur.get('children').models[i]
                var temp =  path.slice(0)
                temp.push(cur2)
                var n = openPathToTarget(cur2, target, temp)


            }
        }


    }

    var nodePosition = function(cur, target, change, pointer){
        var doWork = false
        var siblingSet = []
        for (var i in cur.get('children').models){
            var cur2 = cur.get('children').models[i]
            siblingSet[siblingSet.length] = cur2
            if (doWork == false && cur2!=target){
                nodePosition(cur2, target, change, pointer)
            } else {
                doWork = true
            }
        }
        var last
        if (doWork){

            for (var key in siblingSet){
                key = parseInt(key)
                var val = siblingSet[key]
                if (val == target){
                    if (change == -1){
                        siblingSet[key] = last
                        siblingSet[key-1] = val

                        siblingSet[key].set('hasRight', key < (siblingSet.length-1), {silent: true})
                        siblingSet[key-1].set('hasLeft', (key-1) != 0, {silent: true})
                        siblingSet[key-1].set('hasRight', true, {silent: true})
                        siblingSet[key].set('hasLeft', true, {silent: true})
                        break;

                    } else if (change==1){
                        siblingSet[key] =  siblingSet[key+1]
                        siblingSet[key+1]= val

                        siblingSet[key+1].set('hasRight', (key + 1) < (siblingSet.length-1), {silent: true})
                        siblingSet[key].set('hasLeft', key != 0, {silent: true})
                        siblingSet[key].set('hasRight', true, {silent: true})
                        siblingSet[key+1].set('hasLeft', true, {silent: true})
                        break;


                    }
                }

                         last = val

            }
            pointer.parent = cur
            pointer.child = siblingSet

        }

    }
    var findCurNode = function(me){

        if (me.get('children')){
            var toCheck = []
            for (var x in me.get('children').models){
                var cur = me.get('children').models[x]
                if (cur.get('hideChildren')=="false"){
                    toCheck.push(cur)

                }
            }
            var ret = []
            if (toCheck.length == 0){
                 ret.push(me.get('nodeID'))
            }

            for (x in toCheck){
                var cur = toCheck[x]
                ret = ret.concat(findCurNode(cur))
            }
            return ret


        }
    }

    var hideSiblingsRecur = function(me, toHide){
        //var tar = _.indexOf(me.get('children').models, toHide)
	var tar = _.indexOf(me.get('children').models, toHide)
        for (var i in me.get('children').models){
                if (tar != - 1){
                     if (i != tar){
                        recursiveCollapse(me.get('children').models[i])
                     }
                }
                else {
                    hideSiblingsRecur(me.get('children').models[i], toHide)
                }
        }
    }

    var recursiveCollapse= function(node){
        node.set('hideChildren', "true", {silent: true})

        _.each(node.attributes.children.models, function(cur){
            recursiveCollapse(cur)
        })

    }


    var TreeModel = Backbone.Model.extend({
        elPairs: [],
        url: function() {

            return '/tree?' + decodeURIComponent($.param(contextModel.toParams()));
        },
        changeNodePosition: function(target, change){
            var pointer = {}
            var r = nodePosition(this, target, change, pointer)
            var parent = pointer.parent
            var children = pointer.child
            parent.set('children', new Backbone.Collection(children), {silent: true})
            this.trigger('propagate')
        },
        getShareCode: function(){
            var nodes = findCurNode(this)
            var nodestr = ""
            for (var i in nodes){
                var cur = nodes[i]
                nodestr += "-" + cur
            }
            if (contextModel.get('page') == "pathEditor"){
                Backbone.history.navigate("pathwayeditor/"+contextModel.get('pathid')+ "/node/" + nodestr);
            } else {
                 Backbone.history.navigate("pathway/"+contextModel.get('pathid')+ "/node/" + nodestr);
            }
            contextModel.set('code', nodestr)

        },
        getPathToIDS: function(ids){
            this.collapse(this)
            for (var i in ids){
                var cur = ids[i]
                openPathToTarget(this, parseInt(cur), [this])
            }
            this.trigger('propagate')
        },
        initialize: function(){

            this.set('triggers', new Backbone.Collection())
            this.set('tooltip', 'triggers tooltip')
            this.set('children', new NodeList())
            this.set('sidePanelText', "")
            this.set('name', "Triggers")
            var that = this
            contextModel.on('change:page', function(){
                that.trigger('propagate')
            })
            contextModel.on('change:pathid', function(){
                that.fetch()
                if (contextModel.get('page') == 'pathEditor')
                    Backbone.history.navigate("pathwayeditor/"+contextModel.get('pathid')+ "/node/" + contextModel.get('code'));
                else {
                    Backbone.history.navigate("pathway/"+contextModel.get('pathid')+ "/node/" + contextModel.get('code'));
                }
            }, {success: function(){
                that.collapse(that)
                var openNodes = contextModel.get('code').split('-')
                that.getPathToIDS(openNodes)
            }})
            contextModel.on('change:code', function(){
                var openNodes = contextModel.get('code').split('-')
                that.getPathToIDS(openNodes)

            })
            this.on('sync', function(){
                setTimeout(function(){

                    var openNodes = contextModel.get('code').split('-')
                    that.getPathToIDS(openNodes)
                }, 20);


            })
            this.fetch();
            this.elPairs = []

        },
        getNextNodeID: function(){
            this.set('nodeCount', this.get('nodeCount')+1, {silent: true})
            return this.get('nodeCount')
        },
        hideSiblings: function(toHide){
            hideSiblingsRecur(this, toHide)
        },
        collapse: function(node){
          if (!node){
             recursiveCollapse(this)
          } else {
              recursiveCollapse(node)
          }
        },


        deleteNode: function(toDelete, saveChildren){

                       deleteRecur(this, toDelete, saveChildren)

            this.trigger('propagate')
        },
        getNodeType: function(){
          return "treeModel"
        },
        toJSON: function(){
            var retMap = _.omit(this.attributes, ['children', 'hideChildren', 'selectedNode'])
            retMap.children = this.get('children').toJSON()
            return retMap
        },


        loadNewPathway: function(params){

            this.set('triggers', new Backbone.Model(), {silent: true})
            this.set('sidePanelText', "",  {silent: true})
            this.set('tooltip', params.tooltip, {silent: true})
            this.set('children', new NodeList(), {silent: true})
            this.set('name', params.name, {silent: true})
            this.set('protocol', null, {silent: true})
            this.set('nodeCount', 0, {silent: true})
            this.set('nodeID', this.getNextNodeID(), {silent: true})

            this.unset('id', {silent: true})
            var that = this
            this.save({}, {success: function(){
                    pathwayCollection.fetch()
                }
            })

        },
        parse: function(response){
            if (!response.nodeCount){
                this.set({nodeCount: 0}, {silent: true})
            } else {
                this.set('nodeCount', response.nodeCount, {silent: true})
            }
            if (!response.nodeID){
                this.set('nodeID', this.getNextNodeID(), {silent: true})
            } else {
                this.set('nodeID', response.nodeID, {silent: true})
            }
            this.set({tooltip: response.tooltip}, {silent: true})
            this.set({sidePanelText: response.sidePanelText}, {silent: true})
            this.set({id: response.pathid}, {silent: true})
            this.set({protocol: response.protocol}, {silent: true})
            this.set({name: response.name}, {silent: true})
            var newChildren = new NodeList()
            newChildren.populate(response.children, this)
            this.set({children: newChildren}, {silent: true})
            this.set({hideChildren: "false"}, {silent: true})
            this.once('sync',  function(){recursiveCollapse(this)}, this)
            var triggers = new Backbone.Model()
            _.each(response.triggers, function(value, key){
                var curCollection = new Backbone.Collection(value)
                triggers.set(key, curCollection)

            })
            this.set({triggers: triggers}, {silent: true})

        }

    })
    treeModel = new TreeModel()
    return treeModel

});
