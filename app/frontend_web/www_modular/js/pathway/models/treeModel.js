define([
    'jquery',
    'underscore',
    'backbone',
    'globalmodels/contextModel',
    'pathway/models/nodeModel',
    'pathway/models/pathwayCollection',
    'pathway/models/treeContext',
    'pathway/models/triggerGroupCollection'
], function($, _, Backbone, contextModel, nodeModel, pathwayCollection, triggerGroupCollection){
    var treeModel;

    var deleteRecur = function(me , toDelete, saveChildren){
        if (!me.get('isProtocol')){
            for (var i in me.get('children').models){
                var cur = me.get('children').models[i]
                if (cur == toDelete){
                    var startLoc = me.get('children').indexOf(cur)
                    if (saveChildren){
                       var savedChildren =  cur.get('children').models
                       for (var i in savedChildren){
                           var cur2 = savedChildren[i]
                           if (me.get('children').length == 1 || !cur2.get('isProtocol')){
                               me.get('children').add(cur2, {at: startLoc, silent: true})
                               startLoc = startLoc+1
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

    var openPathToTarget = function(cur, target, path){

        if (cur.get('nodeID') == target){
            for (var i in path){
                var cur2 = path[i]
		cur2.showChildren()
            }

        } else {
            var list = []
            if (!cur.get('isProtocol')) {
            for (var i in cur.get('children').models){
                var cur2 = cur.get('children').models[i]
                var temp =  path.slice(0)
                temp.push(cur2)
                var n = openPathToTarget(cur2, target, temp)
            }


            }
        }


    }

    var nodePosition = function(cur, target, change, pointer){

        var doWork = false
        var siblingSet = []
        if (cur.get('isProtocol')) return
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

        if (!me.get('isProtocol')){
            var toCheck = []
            for (var x in me.get('children').models){
                var cur = me.get('children').models[x]
                if (cur.childrenHidden && !cur.childrenHidden()){
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


        } else {
            return ([me.get('nodeID')])
        }
    }

    var hideSiblingsRecur = function(me, toHide){

          if (me.get('isProtocol')) return


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


        if (node.get('isProtocol')) return
        node.hideChildren()
        _.each(node.attributes.children.models, function(cur){
            recursiveCollapse(cur)
        })

    }


    var TreeModel = nodeModel.extend({
        elPairs: [],
	idAttribute: 'pathid',
        urlRoot: '/tree',
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
	    if (!ids) {
                ids = contextModel.get('code').split('-')
	    }
            for (var i in ids){
                var cur = ids[i]
                if (cur)
                      openPathToTarget(this, (cur), [this])
            }
        },
        initialize: function(){
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
            contextModel.on('change:page', function(){
                treeContext.trigger('propagate')
            })
            contextModel.on('change:pathid', function(){
		var newpathid = contextModel.get('pathid')
                if (newpathid && newpathid != '0') {
		    treeContext.clear()
		    that.getPathToIDS()
		    var oldpathid = that.get('pathid')
		    that.set({pathid:newpathid},{silent:true})
		    if (newpathid != oldpathid) {that.fetch()}
		}
                if (contextModel.get('page') == 'pathEditor') {
                    require(['ckeditor'], function(){})
                    Backbone.history.navigate("pathwayeditor/"+newpathid+ "/node/" + contextModel.get('code'));
                } else {
                    Backbone.history.navigate("pathway/"+newpathid+ "/node/" + contextModel.get('code'));
                }
            })
            contextModel.on('change:code', function(){
                that.getPathToIDS()
		treeContext.trigger('propagate')
            })
	    this.on('propagate', function() {
		if(this.oldContent!=JSON.stringify(this.toJSON())) {
		    this.save()
		} else {
		    treeContext.trigger('propagate')
		}
	    }, this)
            this.on('sync', function(obj, data){
		this.oldContent = JSON.stringify(this.toJSON())
		this.set({'pathid': data.pathid}, {silent:true})
		contextModel.set({'pathid': String(data.pathid)})
		pathwayCollection.fetch()
		this.getPathToIDS()
		treeContext.trigger('propagate')
            }, this)
	    if (contextModel.get('pathid')) {
		that.set({pathid:contextModel.get('pathid')},{silent:true})
		this.getPathToIDS()
		this.fetch()
		treeContext.trigger('propagate')
	    }
            if (contextModel.get('page') == 'pathEditor') {
                require(['ckeditor'], function(){})
            }
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
	    this.save()
        },
        getNodeType: function(){
          return "treeModel"
        },
        toJSON: function(options){
	    if (!options) {options={}}
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
            console.log('the json will look like', retMap)

            return retMap
        },


        loadNewPathway: function(params, options){

            this.set({
		'triggers': new Backbone.Model(),
		'sidePanelText': "",
		'tooltip': params.tooltip,
		'name': params.name,
		'protocol': null,
		'nodeCount': 0,
		'nodeID': 0
	    }, {silent: true})
	    this.populateChildren()

            this.unset('pathid', {silent: true})
	    var that = this
            this.save({}, {success: function(ogj, data){
                    pathwayCollection.fetch()
		    params.pathid = data.pathid
		    if (options && options.toImport) {
			that.parse(params, options)
			that.save ({}, 
				  {success: function(){
				      contextModel.set({'pathid': that.get('pathid')})
				      Backbone.history.navigate("pathwayeditor/"+that.get('pathid')+ "/node/undefined");		    
				      pathwayCollection.fetch()
				  }})			  

		    } else {
			contextModel.set({'pathid': data.pathid})
			Backbone.history.navigate("pathwayeditor/"+that.get('pathid')+ "/node/undefined");		    
			pathwayCollection.fetch()
		    }
            }
			  })

        },
        parse: function(response, options){
	    if (options && options.toImport) {
		response = _.omit(response, ['nodeID', 'nodeCount'])
	    }
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
            this.set({
		tooltip: response.tooltip,
		sidePanelText: response.sidePanelText,
		pathid: response.pathid,
		protocol: response.protocol,
		name: response.name
	    }, {silent: true})
	    	    this.populateChildren(response.children, options)

        this.set('triggers', new triggerGroupCollection(response.triggers));



/*
        console.log('testing', typeof(triggerJSON))
        if (!Object.prototype.toString.call( triggerJSON ) === '[object Array]' ){
            var theGroup = new Backbone.Model()
            for (var n in triggerJSON){
                triggerJSON[n] = new Backbone.Collection(triggerJSON[n])
            }
            theGroup.set({details: new Backbone.Model(triggerJSON), relationship: 'and'})

            result =  new Backbone.Collection([theGroup])
        } else {
            for (var i in triggerJSON){
                var cur = triggerJSON[i]
                var curGroup = new Backbone.Model()
                curGroup.set('relationship', cur.relationship)

                var detailsModel = new Backbone.Model()
                    for (var i2 in cur.details){
                       detailsModel.set(i2, cur.details[i2])
                        for (var i3 in detailsModel.attributes){
                             detailsModel.set(i3, new Backbone.Collection(detailsModel.get(i3)))
                         }
                    }
                curGroup.set('details', detailsModel)

                result.add(curGroup)
            }
         }
            this.set('triggers', result, {silent: true})
*/

        }

    })


    treeModel = new TreeModel()
    return treeModel

});
