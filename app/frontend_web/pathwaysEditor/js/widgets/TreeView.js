define([
    'jquery',     // lib/jquery/jquery
    'underscore', // lib/underscore/underscore
    'backbone',    // lib/backbone/backbone
    'models/contextModel',
    'models/treeModel',
    'internalViews/triggerNode',
    'Helpers',
    'text!templates/treeTemplate.html',
     ],

    function($, _, Backbone, contextModel, curTree, TriggerNode, Helpers, treeTemplate){

        var TreeView = Backbone.View.extend({
            template: _.template(treeTemplate),
            initialize: function(){
                var resizetimer
                 var that = this

               window.onresize = function(){

                    window.clearTimeout(resizetimer)
                    resizetimer = window.setTimeout(function(){
                        that.render()
                    }, 100)
               }
                curTree.on('sync', function(){
                    this.render()
                },this )
               this.render()
            },
            render: function(){
               this.$el.html(this.template())
               $('#saveTreeButton', this.$el).on('click', this.saveTreeFunction)
               $('#loadTreeButton', this.$el).on('click', this.loadTreeFunction)
               var that = this

                $('.tree', that.$el).append("<div style= 'width:auto' class='nodeEl'></div>")
                $('.tree', that.$el).append("<div style='height:60px'></div>")
                var topLevel = new TriggerNode({el:$('.nodeEl').last(), model: curTree});




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
            },
            loadTreeFunction: function(){
                contextModel.set('id', parseInt($('#idcode').val()))
                curTree.fetch()

            },
            saveTreeFunction: function(){
                curTree.save()
            }


        })

        return TreeView
    });






