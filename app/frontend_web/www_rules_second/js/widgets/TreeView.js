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

                $('#hide-tree').on('click', function(){
                    that.render()
                })
                console.log($('#hide-tree'))
                var that = this
            },
            render: function(){
               this.$el.html(this.template())

               var allNodes = []
               var that = this
               this.usableKeys =[]
                for (var key in curRule.attributes){
                     if (Helpers.notDetail.indexOf(key)==-1){

                       this.usableKeys.push(key)
                       console.log(key)

                        console.log(this.usableKeys)
                     }
                }

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
                this.genNodes(this.usableKeys.pop(), this.usableKeys, allNodes, this)



            },

            genNodes: function(head, tail, all, that){
                  require (['text!/templates/DecisionTree/' + head + 'Tree.html'], function(head) {return  function(curTemplate){
                         var temp = _.template(curTemplate)
                        for (var i in curRule.get(head).models){
                            var cur = curRule.get(head).models[i]
                            var text = temp(cur.attributes)
                            $('.tree', that.$el).append("<div style= 'width:300px' class='nodeEl'></div>")
                            var truthLabel = true
                            console.log(cur.get('exists'))
                            if (cur.get('exists') == "false"){
                                truthLabel = false
                            }
                            console.log("creating a node with truthstatus", truthLabel)
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
                for (var i=0;i<nodeList.length-1;i++){
                   var cur = nodeList[i]
                   var next = nodeList[i+1]
                   cur.exitPoint.repaint()
                   next.entryPoint.repaint()
                   cur.negativePoint.repaint()
                    console.log("cur", cur)
                    console.log("next", next)
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






