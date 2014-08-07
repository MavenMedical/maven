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
                curTree.on('propagate', this.render, this)
                curTree.on('sync', function(){
                    this.render()
                },this )
               this.render()
            },
            render: function(){
               curTree.elPairs=[]
               this.$el.html(this.template())
               $('#saveTreeButton', this.$el).on('click', this.saveTreeFunction)
               $('#loadTreeButton', this.$el).on('click', this.loadTreeFunction)

               var that = this

                $('.tree', that.$el).append("<div style= 'width:auto' class='nodeEl'></div>")
                $('.tree', that.$el).append("<div style='height:60px'></div>")
                console.log('the tree will contain', curTree)
                var topLevel = new TriggerNode({el:$('.nodeEl').last(), model: curTree});
                 _.each(curTree.elPairs, function(cur){
                  if(!cur.source.model.get('hideChildren') || cur.source.model.get('protocol')){
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






