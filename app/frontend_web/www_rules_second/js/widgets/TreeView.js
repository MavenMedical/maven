/* A Backbone view which displays the decision tree represented by a rule

 */
define([
    'jquery',     // lib/jquery/jquery
    'underscore', // lib/underscore/underscore
    'backbone',    // lib/backbone/backbone
    'models/contextModel',
    'models/ruleModel',
    'internalViews/treeNode',
    'Helpers',
    'text!templates/DecisionTree/treeTemplate.html',
    'text!templates/DecisionTree/sexTree.html',
    'text!templates/DecisionTree/ageTree.html',
    'text!templates/DecisionTree/triggerTree.html'
     ],

    function($, _, Backbone, contextModel, curRule, treeNode, Helpers, treeTemplate,  sexTree, ageTree, triggerTree){




        var TreeView = Backbone.View.extend({
            template: _.template(treeTemplate),
            initialize: function(){
                //declare the resize timer this will rerender the frame on resize but only if 100ms pass without
                //another resize
                var resizetimer


                 var that = this
                //cant prerender this tab because of jsplumb's inability to paint on hidden els
                //instead render when the tab finsihes being shown
                $('#hide-tree').on('shown.bs.tab', function(){
                    that.render()
                })
                //when the window is resized
               window.onresize = function(){
                    //end the current timer on the window
                    window.clearTimeout(resizetimer)
                   //create a new 100 ms timer on the window which will rerender the frame
                    resizetimer = window.setTimeout(function(){
                        that.render()
                    }, 100)
               }
               //rerender when a new rule is selected
               curRule.on('selected', function(){that.render()})

            },
            render: function(){

               this.$el.html(this.template())
                //this array will contain all the nodes as we create them so we can paint the jsplumb on them at the end
               var allNodes = []
               var that = this
                //this array will fetch all of the detail keys that are used by the rule so we can create the nodes
                //for each
               this.usableKeys =[]
                for (var key in curRule.attributes){
                    //dont take keys that arent for details
                    if (Helpers.notDetail.indexOf(key)==-1){

                       this.usableKeys.push(key)

                     }
                }
                //create a spot for the trigger node
                $('.tree', that.$el).append("<div style= 'width:300px' class='nodeEl'></div>")
                $('.tree', that.$el).append("<div style='height:60px'></div>")
                var tx = ""

                var triggers = curRule.get('triggers')
                //set the text of the trigger node based on whether its a drug or procedure rule
                if (curRule.get('triggerType') == 'HCPCS'){
                    tx +="Is the clinician ordering any of the following procedures: "
                } else {
                    tx +="Is the clinician ordering any of the following drugs: "
                }
                //add the text for all of the triggers to the text set
                for (var i in triggers.models){
                    var cur = triggers.models[i]
                    tx += "<br><b>" + cur.get('term') +"</b>"
                    if (curRule.get('triggerType') == "NDC"){
                        tx+=" via the route: <b>"
                        if (cur.get('route')=='%'){
                            tx+="ANY"
                        } else {
                            tx +=cur.get('route')
                        }
                        tx+="</b><br>"
                    }
                }
                //create new tree node to be rendered in the new el with the trigger heading and text
                //its veracity is true because the down arrow is YES
                allNodes.push(new treeNode({el:$('.nodeEl').last(), text:tx, veracity: true}))

                //create a node for age restriction if there is one
                if (curRule.get('minAge')>0 || curRule.get('maxAge')<200){
                    //create the spot
                    $('.tree', that.$el).append("<div style= 'width:300px' class='nodeEl'></div>")
                    $('.tree', that.$el).append("<div style='height:60px'></div>")
                    //create the node and push it to the set
                    allNodes.push(new treeNode({el:$('.nodeEl').last(), text:(_.template(ageTree))(curRule.attributes), veracity: true}))
                }
                //create the node for gender restriction if there is one
                if (curRule.get('genders')!="%"){
                    //create the spot
                    $('.tree', that.$el).append("<div style= 'width:300px' class='nodeEl'></div>")
                    $('.tree', that.$el).append("<div style='height:60px'></div>")
                    //create the node and push it to the set
                    allNodes.push(new treeNode({el:$('.nodeEl').last(), text: (_.template(sexTree))(curRule.attributes), veracity: true}))
                }
                //if there are no dertails, draw the connections now
                if (this.usableKeys==0){

                    this.drawConnections(allNodes)

                }
                //if there are details, begin recursion to generate the nodes
                else{
                    this.genNodes(this.usableKeys.pop(), this.usableKeys, allNodes, this)
                 }


            },
            //the recursive nature of this function is required to allow the next instance of it to trigger
            //when the require finishes instead of when the function finishes executing as would happen in
            //a loop
            genNodes: function(head, tail, all, that){
                //get the tree node template for the current head of the list
                require (['text!/templates/DecisionTree/' + head + 'Tree.html'], function(head) {return  function(curTemplate){

                         var temp = _.template(curTemplate)
                        //for each detail of the current detail type
                        for (var i in curRule.get(head).models){
                            var cur = curRule.get(head).models[i]
                            //the text of its node is the attributes of the model in the current template
                            var text = temp(cur.attributes)

                            //create the spot for the node
                            $('.tree', that.$el).append("<div style= 'width:300px' class='nodeEl'></div>")
                            //set the veracity of the new node based on the 'exists' attribute of the detail
                            //if there is no exists attribute, default to to true
                            var truthLabel = true
                            if (cur.get('exists') == "false"){
                                truthLabel = false
                            }
                            //create the new node
                             var testNode = new treeNode({el:$('.nodeEl').last(), text:text, veracity: truthLabel})
                            //add the new node to the node list
                            all.push(testNode)
                             //create the padding for the node
                             $('.tree', that.$el).append("<div style='height:60px'></div>")
                        }
                         //RECURSIVE STEP
                         //if there are more nodes, pop one off as the head, the remainder as the tail,
                         // pass the list we are currently building
                         //also pass the referance to the tree view
                         if(tail.length >0) {
                             that.genNodes(tail.pop(), tail, all, that)
                         } else {
                         //if the list of detail types is now empty time to draw the connections
                             that.drawConnections(all)
                         }
                  };}(head));

            },
            //draw the connections with jsplumb for each node in the list
            drawConnections: function(nodeList){
                //put endpoints on the ending nodes (the ones that say "alert clinician" and "dont alert the clinician"
                //the last tree nodes will connect to their top's so anchor the endpoints on top
                var trueFinish = jsPlumb.addEndpoint($('#doRule'), {anchor: "Top"})
                var falseFinish = jsPlumb.addEndpoint($('#dontRule'), {anchor:"Top"})
                //if the node list is of length one we know its just the trigger node
                if (nodeList.length == 1){

                    //repaint the trigger node, in case something has caused it to move
                    nodeList[0].exitPoint.repaint




                    //just draw the line from the trigger nodes bottom to the top of the true finish
                    jsPlumb.connect({
                                     source: nodeList[0].exitPoint,
                                     target: trueFinish,
                                     overlays:nodeList[0].posOverlay
                    })
                    //and from the trigger nodes right side to the false finish
                    jsPlumb.connect({
                                    source: nodeList[0].negativePoint,
                                    target: falseFinish,
                                    overlays:nodeList[0].negOverlay
                    })


                }

                //if theres more than one node we need to loop, loop from the first node to the second to last node
                for (var i=0;i<nodeList.length-1;i++){
                    //take the current node
                   var cur = nodeList[i]
                    //take the next node
                   var next = nodeList[i+1]

                   //we are about to draw  connections so lets make sure the source and target are in the right place
                   //using repaint
                   cur.exitPoint.repaint()
                   next.entryPoint.repaint()
                   cur.negativePoint.repaint()

                    //draw a line from the bottom of the current node to the top of the next node, its overlay
                    //will say YES or NO depending on the curren nodes veracity
                    jsPlumb.connect({source: cur.exitPoint,
                                    target: next.entryPoint,
                                    overlays: cur.posOverlay
                   })
                    //likewise draw a line from the current nodes right side to the false finish
                    //its overlay is the opposite of the other one
                   jsPlumb.connect({source: cur.negativePoint,
                                    target: falseFinish,
                                    overlays:cur.negOverlay})
                    //if this is the second to last node in the list
                   if (i+2 == nodeList.length){
                       next.exitPoint.repaint()
                        //draw a line from the bottom of the 'next' node to the top of the true finish
                       jsPlumb.connect({
                                            source: next.exitPoint,
                                            target: trueFinish,
                                            overlays:next.posOverlay})
                       //draw a line from the right of the 'next' node to the top of the false finish
                        jsPlumb.connect({
                                    source: next.negativePoint,
                                    target: falseFinish,
                                    overlays:next.negOverlay})
                   }

                    }
            }
        })

        return TreeView
    });






