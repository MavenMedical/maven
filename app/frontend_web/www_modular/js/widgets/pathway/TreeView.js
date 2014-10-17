define([
    'jquery',     // lib/jquery/jquery
    'underscore', // lib/underscore/underscore
    'backbone',    // lib/backbone/backbone
    'globalmodels/contextModel',
    'pathway/models/treeModel',
    'pathway/internalViews/triggerNode',
    'pathway/modalViews/nodeEditor',
    'pathway/Helpers',
    'pathway/models/pathwayCollection',
    'text!templates/pathway/treeTemplate.html',
    'text!templates/pathway/insertDiv.html'
],

    function ($, _, Backbone, contextModel, curTree, TriggerNode, NodeEditor, Helpers, pathwayCollection, treeTemplate, insertDiv) {

        var TreeView = Backbone.View.extend({

            insertTemplate: _.template(insertDiv),
            template: _.template(treeTemplate),
            initialize: function () {
                this.$el.html(this.template())
                this.plumb = jsPlumb.getInstance({
                    MaxConnections: -1,
                    Connector: [ "Flowchart", { cornerRadius: 3 }],
                    Endpoint: 'Blank',
                    PaintStyle: {
                        lineWidth: 2,
                        strokeStyle: '#ccc'
                    },
                    HoverPaintStyle: {
                        lineWidth: 2,
                        strokeStyle: '#61B7CF'
                    }

                })

                this.treeEl = $('.tree', this.$el)
                this.el.onclick = function(param1){
                     var target = $(param1.explicitOriginalTarget)
                    console.log(target.closest('.click-tracked'))
                      if (target.closest('.click-tracked').length){
                          var id = target.closest('.click-tracked').attr('clickid')
                          /*
                                click tracking code goes here
                           */


                      }
                }
                this.treeEl.draggable()
                var that = this
                this.plumb.setContainer(this.treeEl[0])
                this.$el.on('wheel', function (data) {
                    data.preventDefault()
                    /*
                     */
                    var re = /scale\((.*)\)/
                    var n = that.treeEl[0].style.transform
                    var result = re.exec(n)
                    if (data.originalEvent.deltaY > 0) {
                        var newScale = result[1] - .05
                    } else {
                        var newScale = (result[1] - 0) + .05

                    }
                    var scaleString = 'scale(' + newScale + ')'
                    that.treeEl.css({'transform': scaleString})

                })

                var resizetimer
                var that = this
                window.onresize = function () {

                    window.clearTimeout(resizetimer)
                    resizetimer = window.setTimeout(function () {
                        that.render()
                    }, 100)
                }
                curTree.on('propagate', function () {
                    that.render();
                }, this)
                curTree.on('sync', this.render, this)
                contextModel.on('change', this.render, this)
                this.render()
            },
            render: function () {
                curTree.elPairs = []
                this.plumb.deleteEveryEndpoint();
                this.treeEl.html('')
                $('#drawPaths', this.$el).on('click', function () {
                    this.render();
                })
                var that = this
                $('.tree', that.$el).append("<div style= 'width:auto; height: auto' class='nodeEl'></div>")
                $('.tree', that.$el).append("<div style='height:100px'></div>")

                var topLevel = new TriggerNode({el: $('.nodeEl', this.$el).last(), model: curTree});

                if(curTree.attributes.name == "Triggers" && contextModel.get('page') == 'pathway'){
                     $("#welcome-modal").modal({'show': 'true'});
                }

                if (contextModel.get('page') == 'pathEditor')
                    $('#pathwayName').html("Now Editing Pathway: " + curTree.attributes.name);
                else {
                    $('#pathwayName').html("")
                }

                 var insertDiv = Backbone.View.extend({
                     initialize: function(params){

                        this.$el.html("<div style='float: left; background-color: white; height: 15px'>+</div>")
                        this.parentNode = params.source
                        this.childNode = params.target
                        var that = this
                        this.$el.on('click', function(){

                             var newEditor = new NodeEditor(that.parentNode, that.childNode)


                        })


                     }



                 })
                for (var i in curTree.elPairs) {
                    var cur = curTree.elPairs[i]
                    if ((cur.source.$el.is(":visible")) && (cur.target.$el.is(":visible"))) {

                        var a = cur.source.makeExit(that.plumb)
                        var b = cur.target.makeEntrance(that.plumb)

                        if (cur.bold) {
                            that.plumb.connect({
                                source: a,
                                target: b,
                                 overlays:[
                                    ["Custom", {
                                      create:function(component) {

                                          console.log("the source", cur.source)
                                         var myInsert = new insertDiv({source: cur.source.model, target: cur.target.model})

                                         if (contextModel.get('page')=='pathEditor'){
                                             return myInsert.$el
                                         } else {
                                               return $("<div></div>")
                                         }
                                      },
                                        location: -10 ,

                                      id:"customOverlay"
                                    }]
                                  ],
                                paintStyle: {
                                    lineWidth: 4,
                                    strokeStyle: '#46bdec'
                                }
                            })
                        } else {
                            that.plumb.connect({

                                overlays:[
                                    ["Custom", {
                                      create:function(component) {

                                         console.log("the source", cur.source)
                                         var myInsert = new insertDiv({source: cur.source.model, target: cur.target.model})
                                         if (contextModel.get('page')=='pathEditor'){
                                             return myInsert.$el
                                         } else {
                                               return $("<div></div>")
                                           }
                                      },
                                        location: -10 ,

                                      id:"customOverlay"
                                    }]
                                  ],
                                source: a,
                                target: b
                            })
                        }
                    }
                }

                contextModel.trigger('rendered')

            },
            showExtraInfo: function(){

            },
            drawNodes: function () {


            },
            saveTreeFunction: function () {
                curTree.save()
            }
        })

        return TreeView
    });






