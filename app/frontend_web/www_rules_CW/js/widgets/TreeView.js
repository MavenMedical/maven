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
                var resizetimer
                 var that = this
                $('#hide-tree').on('shown.bs.tab', function(){
                    that.render()
                })
               window.onresize = function(){

                    window.clearTimeout(resizetimer)
                    resizetimer = window.setTimeout(function(){
                        that.render()
                    }, 100)
               }
               curRule.on('selected', function(){that.render()})

            },
            render: function(){
               this.$el.html(this.template())

               var allNodes = []
               var that = this
               this.usableKeys =[]
                for (var key in curRule.attributes){
                     if (Helpers.notDetail.indexOf(key)==-1){

                       this.usableKeys.push(key)

                     }
                }
                $('.tree', that.$el).append("<div style= 'width:300px' class='nodeEl'></div>")
                $('.tree', that.$el).append("<div style='height:60px'></div>")
                var tx = ""
                var triggers = curRule.get('triggers')
                if (curRule.get('triggerType') == 'HCPCS'){
                    tx +="Is the clinician ordering any of the following procedures: "
                } else {
                    tx +="Is the clinician ordering any of the following drugs: "
                }
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

                allNodes.push(new treeNode({el:$('.nodeEl').last(), text:tx, veracity: true}))
                if (curRule.get('minAge')>0 || curRule.get('maxAge')<200){
                    $('.tree', that.$el).append("<div style= 'width:300px' class='nodeEl'></div>")
                    $('.tree', that.$el).append("<div style='height:60px'></div>")
                    allNodes.push(new treeNode({el:$('.nodeEl').last(), text:(_.template(ageTree))(curRule.attributes), veracity: true}))
                }
                if (curRule.get('genders')!="%"){
                    $('.tree', that.$el).append("<div style= 'width:300px' class='nodeEl'></div>")
                    $('.tree', that.$el).append("<div style='height:60px'></div>")

                    allNodes.push(new treeNode({el:$('.nodeEl').last(), text: (_.template(sexTree))(curRule.attributes), veracity: true}))
                }
                if (this.usableKeys==0){
                    this.drawConnections(allNodes)
                } else{
                    this.genNodes(this.usableKeys.pop(), this.usableKeys, allNodes, this)
                 }


            },

            genNodes: function(head, tail, all, that){
                  require (['text!/templates/DecisionTree/' + head + 'Tree.html'], function(head) {return  function(curTemplate){
                         var temp = _.template(curTemplate)
                        for (var i in curRule.get(head).models){
                            var cur = curRule.get(head).models[i]
                            var text = temp(cur.attributes)
                            $('.tree', that.$el).append("<div style= 'width:300px' class='nodeEl'></div>")
                            var truthLabel = true
                            if (cur.get('exists') == "false"){
                                truthLabel = false
                            }
                             var testNode = new treeNode({el:$('.nodeEl').last(), text:text, veracity: truthLabel})
                             all.push(testNode)
                             $('.tree', that.$el).append("<div style='height:60px'></div>")
                        }
                         if(tail.length >0) {
                             that.genNodes(tail.pop(), tail, all, that)
                         } else {
                             that.drawConnections(all)
                         }
                  };}(head));

            },

            drawConnections: function(nodeList){
                var trueFinish = jsPlumb.addEndpoint($('#doRule'), {anchor: "Top"})
                var falseFinish = jsPlumb.addEndpoint($('#dontRule'), {anchor:"Top"})
                if (nodeList.length == 1){
                    nodeList[0].exitPoint.repaint
                    jsPlumb.connect({
                                     source: nodeList[0].exitPoint,
                                     target: trueFinish,
                                     overlays:nodeList[0].posOverlay
                    })
                    jsPlumb.connect({
                                    source: nodeList[0].negativePoint,
                                    target: falseFinish,
                                    overlays:nodeList[0].negOverlay
                    })


                }
                for (var i=0;i<nodeList.length-1;i++){
                   var cur = nodeList[i]
                   var next = nodeList[i+1]
                   cur.exitPoint.repaint()
                   next.entryPoint.repaint()
                   cur.negativePoint.repaint()
                   jsPlumb.connect({source: cur.exitPoint,
                                    target: next.entryPoint,
                                    overlays: cur.posOverlay
                   })
                   jsPlumb.connect({source: cur.negativePoint,
                                    target: falseFinish,
                                    overlays:cur.negOverlay})

                   if (i+2 == nodeList.length){
                       next.exitPoint.repaint()

                       jsPlumb.connect({
                                            source: next.exitPoint,
                                            target: trueFinish,
                                            overlays:next.posOverlay})
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






