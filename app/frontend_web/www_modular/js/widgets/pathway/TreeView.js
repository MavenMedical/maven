define([
    'jquery',     // lib/jquery/jquery
    'underscore', // lib/underscore/underscore
    'backbone',    // lib/backbone/backbone
    'globalmodels/contextModel',
    'pathway/models/treeModel',
    'pathway/internalViews/triggerNode',
    'pathway/Helpers',
    'text!templates/pathway/treeTemplate.html'
     ],

    function($, _, Backbone, contextModel, curTree, TriggerNode, Helpers, treeTemplate){

        var TreeView = Backbone.View.extend({


            template: _.template(treeTemplate),
            initialize: function(){
                  this.$el.html(this.template())
                this.plumb = jsPlumb.getInstance({
                    Connector : "Flowchart",
                    PaintStyle :  { lineWidth : 2, strokeStyle : "#456" },
                    Endpoint : "Blank",
                    MaxConnections  : -1,
                    PaintStyle :  {
                         lineWidth: 2,
                         strokeStyle: '#ccc'
                    },
                    HoverPaintStyle :  {
                         lineWidth: 3,
                         strokeStyle: '#61B7CF'
                    },
                    HoverPaintStyle :  {
                        lineWidth: 3,
                        strokeStyle: '#61B7CF'
                    }
                })

                 this.treeEl = $('.tree', this.$el)
                 this.treeEl.draggable()
                var that = this
                this.plumb.setContainer(this.treeEl[0])
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
                this.plumb.detachEveryConnection();
                this.treeEl.html('')
               $('#drawPaths', this.$el).on('click', function(){
                   this.render();
               })
               var that = this

                $('.tree', that.$el).append("<div style= 'width:auto' class='nodeEl'></div>")
                $('.tree', that.$el).append("<div style='height:60px'></div>")
                var topLevel = new TriggerNode({el:$('.nodeEl', this.$el).last(), model: curTree});
                 _.each(curTree.elPairs, function(cur){

                  if((cur.source.$el.is(":visible")) && (cur.target.$el.is(":visible"))){
                       var a = cur.source.makeExit(that.plumb)
                       var b = cur.target.makeEntrance(that.plumb)
                       that.plumb.connect({
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






