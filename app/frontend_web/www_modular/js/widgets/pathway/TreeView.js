define([
        'jquery',     // lib/jquery/jquery
        'underscore', // lib/underscore/underscore
        'backbone',    // lib/backbone/backbone
        'globalmodels/contextModel',
        'pathway/models/treeModel',
        'pathway/models/treeContext',
        'widgets/pathway/toolbar',
        'pathway/internalViews/triggerNode',
        'pathway/modalViews/nodeEditor',
        'pathway/Helpers',
        'pathway/models/pathwayCollection',
        'text!templates/pathway/treeTemplate.html',
        'text!templates/pathway/insertDiv.html',
        'jsplumb'
    ],

    function ($, _, Backbone, contextModel, curTree, treeContext,toolbar, TriggerNode, NodeEditor, Helpers, pathwayCollection, treeTemplate, insertDiv) {

        var TreeView = Backbone.View.extend({

            template: _.template(treeTemplate),
            initialize: function () {
                this.$el.html(this.template())
                this.toolbar = new toolbar({el:this.$('#pathway-toolbox')})

                if(contextModel.get('page') == 'pathway') {
                    $('.widget-title', this.$el).html('Pathway')
                } else {
                    $('.widget-title', this.$el).html('Pathway Editor')
                }
                contextModel.on('change:page', function () {
                    if (contextModel.get('page') == 'pathEditor' || contextModel.get('page') == 'pathway') {
                        if(contextModel.get('page') == 'pathway') {
                            $('.widget-title', this.$el).html('Pathway')
                        } else {
                            $('.widget-title', this.$el).html('Pathway Editor')
                        }
                        this.$el.show()

                    } else {
                        this.$el.hide()
                    }
                }, this)
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
                var that = this
                setTimeout(function () {
                    that.reset = true;
                    that.adjustWidth()
                }, 500)
                this.treeEl = $('.pathtree', this.$el)
                that.treeEl.css({'opacity': 0})
                this.treeEl.draggable({
                    start: function (event, ui) {
                        treeContext.suppressClick = true
                    },
                    stop: function (event, ui) {
                        setTimeout(function () {
                            treeContext.suppressClick = false
                        }, 100)
                        $(event.toElement).one('click', function (e) {
                            e.stopImmediatePropagation();
                        });
                        that.updateSelectedOffset()
                    }
                })
                var that = this
                this.plumb.setContainer(this.treeEl[0])
                this.$el.on('wheel', function (data) {
                        var mouseX = data.originalEvent.pageX;
                        var mouseY = data.originalEvent.pageY;
                        var left = that.treeEl.offset().left
                        var top = that.treeEl.offset().top
                        data.preventDefault()
                        /*
                         */
                        var re = /scale\((.*)\)/
                        var n = that.treeEl[0].style.transform
                        var transform_property = 'transform';
                        if (!n) {
                            n = that.treeEl[0].style.msTransform;
                            transform_property = 'msTransform'
                        }
                        if (n) {
                            var oldScale = re.exec(n)[1];
                            if (data.originalEvent.deltaY > 0) {
                                var newScale = oldScale - .05
                            } else {
                                var newScale = (oldScale - 0) + .05
                            }
                            var newTop = mouseY - (mouseY - top ) * newScale / oldScale;
                            var newLeft = mouseX - (mouseX - left ) * newScale / oldScale;
                            if (newScale > 5 || newScale <= .25) {
                                return
                            }
                            var scaleString = 'scale(' + newScale + ')'
                            if (transform_property == 'transform') {
                                that.treeEl.css({'transform': scaleString})
                            } else {
                                that.treeEl.css({'msTransform': scaleString})
                            }
                            that.treeEl.offset({left: newLeft,
                                top: newTop});
                            that.setDraggableBox(newScale)
                            that.updateSelectedOffset()
                        }
                    }
                )

                var resizetimer
                window.onresize = function () {

                    window.clearTimeout(resizetimer)
                    resizetimer = window.setTimeout(function () {
                        that.render()
                    }, 100)
                }
                treeContext.on('propagate sync', function () {
                    this.render();
                }, this)
                //contextModel.on('change', this.render, this)
                contextModel.on('change:canonical', function () {
                    treeContext.set({'selectedNodeOffset': null, 'selectedNode': null}, {silent: true})
                    that.treeEl.css({'opacity': 0})
                    that.reset = true
                    if (that.treeEl[0].style.transform) {
                        that.treeEl.css({left: '', top: '', transform: 'scale(1)'});
                    } else {
                        that.treeEl.css({left: '', top: '', msTransform: 'scale(1)'});
                    }
                    setTimeout(function () {
                        that.reset = true;
                        that.adjustWidth()
                    }, 500)
                })
                this.render()
            },
            render: function () {


                var that = this
                if (contextModel.get('page') == 'pathEditor' || contextModel.get('page') == 'pathway') {
                    this.$el.show()
                    this.toolbar.showhide()

                } else {
                    return
                }

                that.treeEl.css({'cursor': 'wait'})

                var pathid = contextModel.get('pathid');
                if (pathid && pathid != '0') {
                    this.$el.show()
                } else {
                    this.$el.hide()
                }
                curTree.elPairs = []
                this.plumb.deleteEveryEndpoint();
                this.treeEl.html('')

                $('.pathtree', that.$el).append("<div style= 'width:auto; height: auto' class='nodeEl'></div>")
                $('.pathtree', that.$el).append("<div style='height:100px'></div>")

                var topLevel = new TriggerNode({el: $('.nodeEl', this.$el).last(), model: curTree});

                if (contextModel.get('page') == 'pathEditor')
                    $('#pathwayName').html("Now Editing Pathway: " + curTree.attributes.name);
                else if (contextModel.get('page') == 'pathHistory')
                    $('#pathwayName').html("Now Viewing History for Pathway: " + curTree.attributes.name);
                else {
                    $('#pathwayName').html("")
                }
                this.renderJSPlumb()
                this.adjustWidth()
                this.setDraggableBox()
            },
            adjustWidth: function () {

                if (this.reset) {
                    var selected = $('.treeNode.selected')
                    if(!selected.length) {selected = $('.protocolNode.selected')}
                    this.reset = false
                    var boundingWidth = $('.nodeEl', this.$el).width()
                    var offset = this.treeEl.offset()
                    var diff = 0
                    if (selected && selected.length==1) {
                        var s_offset = selected.offset()
                        var t_offset = this.treeEl.offset()
                        var w_offset = this.$el.offset()
                        var left_diff = s_offset.left - (w_offset.left + this.$el.width() * 2/3)
                        var top_diff = s_offset.top - (w_offset.top + this.$el.height() * 2/3)
                        if(top_diff > 0) {
                            t_offset.top -= top_diff
                            this.treeEl.offset(t_offset)
                        }
                    }
                    if (left_diff > 0) {
                        t_offset.left -= left_diff
                        this.treeEl.offset(t_offset)
                    } else {
                        var widthDiff = (this.$el.width() - boundingWidth) / 2
                        if (widthDiff > 0) {
                            offset.left = this.$el.offset().left + widthDiff;
                            this.treeEl.offset(offset)
                        }
                    }
                    this.treeEl.css({'opacity': 1})
                }
            },
            setDraggableBox: function (scale) {
                if (!scale) {
                    scale = 1
                }
                var boxnode = $('.nodeEl', this.$el)
                var boundingW = boxnode.width()
                var boundingH = boxnode.height()

                var l = this.$el.offset().left , t = this.$el.offset().top
                var w = this.$el.width(), h = this.$el.height()
                var box = [l + (100 - boundingW) * scale, t + (50 - boundingH) * scale, l + w - 100 * scale, t + h - 100 * scale]
                this.treeEl.draggable('option', 'containment', box)
            },
            renderJSPlumb: function () {
                var that = this
                var insertDiv = Backbone.View.extend({
                    initialize: function (params) {

                        this.$el.html("<div style='float: left; background-color: white; height: 15px'>+</div>")
                        this.parentNode = params.source
                        this.childNode = params.target
                        var that = this
                        this.$el.on('click', function () {

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
                                overlays: [
                                    ["Custom", {
                                        create: function (component) {

                                            var myInsert = new insertDiv({source: cur.source.model, target: cur.target.model})

                                            if (contextModel.get('page') == 'pathEditor' && !contextModel.get('preview')) {
                                                return myInsert.$el
                                            } else {
                                                return $("<div></div>")
                                            }
                                        },
                                        location: -10,

                                        id: "customOverlay"
                                    }]
                                ],
                                paintStyle: {
                                    lineWidth: 4,
                                    strokeStyle: '#46bdec'
                                }
                            })
                        } else {
                            that.plumb.connect({

                                overlays: [
                                    ["Custom", {
                                        create: function (component) {

                                            // console.log("the source", cur.source)
                                            var myInsert = new insertDiv({source: cur.source.model, target: cur.target.model})
                                            if (contextModel.get('page') == 'pathEditor' && !contextModel.get('preview')) {
                                                return myInsert.$el
                                            } else {
                                                return $("<div></div>")
                                            }
                                        },
                                        location: -10,

                                        id: "customOverlay"
                                    }]
                                ],
                                source: a,
                                target: b
                            })
                        }
                    }
                }

                var selected = $('.selected.treeNode')
                var old = treeContext.get('selectedNodeOffset')
                if (old && selected.length && selected.is(':visible') && old.clickid == selected.attr('clickid')) {
                    var tree = this.treeEl.offset();
                    var cur = selected.offset();
                    this.treeEl.offset({left: tree.left - cur.left + old.left,
                        top: tree.top - cur.top + old.top});
                }

                contextModel.trigger('rendered')
                that.treeEl.css({'cursor': 'default'})


            },
            updateSelectedOffset: function() {
                var selected = $('.selected.treeNode')
                if (selected && old && selected.offset()) {
                    var old = treeContext.get('selectedNodeOffset')
                    old.left = selected.offset().left
                    old.top = selected.offset().top
                }
            },
            showExtraInfo: function () {

            },
            drawNodes: function () {


            },
        })

        return TreeView
    });






