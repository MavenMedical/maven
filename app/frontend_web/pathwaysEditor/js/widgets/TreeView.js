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
                 this.treeEl = $('.tree', this.$el)
                 this.treeEl.draggable()

                jsPlumb.setContainer(this.treeEl)
                 var resizetimer
                 var that = this
               window.onresize = function(){

                    window.clearTimeout(resizetimer)
                    resizetimer = window.setTimeout(function(){
                        that.render()
                    }, 100)
               }
                curTree.on('propagate', this.render, this)
                curTree.on('sync', function(){
                    this.render()
                },this )
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


            },

            drawNodes: function(){


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






