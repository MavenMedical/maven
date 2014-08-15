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
                  this.$el.html(this.template())

                 jsPlumb.Defaults.Connector = "Flowchart"
                 jsPlumb.Defaults.PaintStyle=  { lineWidth : 2, strokeStyle : "#456" }
                 jsPlumb.Defaults.Endpoint ="Blank"
                 jsPlumb.Defaults.MaxConnections =-1

                 jsPlumb.Defaults.PaintStyle =  {
                  lineWidth: 2,
                  strokeStyle: '#ccc'
                 },
                  jsPlumb.Defaults.HoverPaintStyle= {
                    lineWidth: 3,
                    strokeStyle: '#61B7CF'
                  },
                 this.treeEl = $('.tree', this.$el)
                 this.treeEl.draggable()
                var that = this

                jsPlumb.setContainer(this.treeEl[0])
                 this.$el.on('wheel', function(data){
                    data.preventDefault()
/*
 */                    var re = /scale\((.*)\)/
                     var n = that.treeEl[0].style.transform
                     var result = re.exec(n)
                     if (data.originalEvent.deltaY > 0){
                         var newScale = result[1] -.05
                     } else {
                          var newScale = (result[1]-0) + .05

                     }
                     var scaleString = 'scale(' + newScale +')'
                     that.treeEl.css({'transform': scaleString})

                 })

                 var resizetimer
                 var that = this
               window.onresize = function(){

                    window.clearTimeout(resizetimer)
                    resizetimer = window.setTimeout(function(){
                        that.render()
                    }, 100)
               }
                curTree.on('propagate', this.render, this)
                curTree.on('sync', this.render, this)
                contextModel.on('change', this.render, this)
               this.render()
            },
            render: function(){
               curTree.elPairs=[]
                jsPlumb.detachEveryConnection();
                this.treeEl.html('')
               $('#drawPaths', this.$el).on('click', function(){
                   this.render();
               })
               var that = this

                $('.tree', that.$el).append("<div style= 'width:auto' class='nodeEl'></div>")
                $('.tree', that.$el).append("<div style='height:60px'></div>")
                var topLevel = new TriggerNode({el:$('.nodeEl').last(), model: curTree});
                 _.each(curTree.elPairs, function(cur){

                  if((cur.source.$el.is(":visible")) && (cur.target.$el.is(":visible"))){
                       var a = cur.source.makeExit()
                       var b = cur.target.makeEntrance()
                       jsPlumb.connect({
                           source: a,
                           target: b,

                           overlays: [["Arrow", {location:1}]]
                       })
                  }
                })

                contextModel.trigger('rendered')
            },

            drawNodes: function(){


            },

            saveTreeFunction: function(){
                curTree.save()
            }


        })

        return TreeView
    });






