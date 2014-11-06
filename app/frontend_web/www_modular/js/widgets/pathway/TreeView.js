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
        'text!templates/pathway/insertDiv.html',
        'jsplumb',
        'ckeditor'
    ],

    function ($, _, Backbone, contextModel, curTree, TriggerNode, NodeEditor, Helpers, pathwayCollection, treeTemplate, insertDiv) {

        var TreeView = Backbone.View.extend({

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
                var that = this
                setTimeout(function () {
                    that.reset = true;
                    that.render()
                }, 200)
                this.treeEl = $('.tree', this.$el)
                that.treeEl.css({'opacity': 0})
                this.treeEl.draggable({
                    start: function (event, ui) {
                        curTree.suppressClick = true
                    },
                    stop: function (event, ui) {
                        setTimeout(function () {
                            curTree.suppressClick = false
                        }, 100)
                        $(event.toElement).one('click', function (e) {
                            e.stopImmediatePropagation();
                        });
                    }
                })
                this.treeEl.click(function (param1) {
                    //Don't track clicks in edit mode (where page would be "pathwayEditor")
                    if (contextModel.get('page') != 'pathway' || curTree.suppressClick) {
                        return;
                    }
                    var target = $(param1.target)
                    console.log(target.closest('.click-tracked'))
                    if (target.closest('.click-tracked').length) {
                        var node_state = (target.closest('.click-tracked').attr('clickid'));

                        var data = { "patient_id": contextModel.get("patients"),
                            "protocol_id": contextModel.get("pathid"),
                            "node_state": node_state,
                            "datetime": (new Date().toISOString()).replace("T", " "),
                            "action": "click" }
                        $.ajax({
                            type: 'POST',
                            dataType: 'json',
                            url: "/activity?" + $.param(contextModel.toParams()),
                            data: JSON.stringify(data),
                            success: function () {
                                console.log("click tracked");
                            }
                        });

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
                curTree.on('propagate', function () {
                    this.render();
                }, this)
                curTree.on('drawJSPlumb', this.renderJSPlumb, this)
                //contextModel.on('change', this.render, this)
                contextModel.on('change:pathid', function () {
                    curTree.set({'selectedNodeOffset': null, 'selectedNode': null}, {silent: true})
                    that.treeEl.css({'opacity': 0})
                    that.reset = true
                    if (that.treeEl[0].style.transform) {
                        that.treeEl.css({left: '', top: '', transform: 'scale(1)'});
                    } else {
                        that.treeEl.css({left: '', top: '', msTransform: 'scale(1)'});
                    }
                })
                this.render()
            },
            render: function () {
                var that = this
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

                $('.tree', that.$el).append("<div style= 'width:auto; height: auto' class='nodeEl'></div>")
                $('.tree', that.$el).append("<div style='height:100px'></div>")

                var topLevel = new TriggerNode({el: $('.nodeEl', this.$el).last(), model: curTree});

                if (contextModel.get('page') == 'pathEditor')
                    $('#pathwayName').html("Now Editing Pathway: " + curTree.attributes.name);
                else {
                    $('#pathwayName').html("")
                }
                this.renderJSPlumb()
                this.adjustWidth()
                this.setDraggableBox()
            },
            adjustWidth: function () {

                if (this.reset) {
                    this.reset = false
                    var boundingWidth = $('.nodeEl', this.$el).width()
                    var widthDiff = (this.$el.width() - boundingWidth) / 2
                    if (widthDiff > 0) {
                        var offset = this.treeEl.offset()
                        offset.left = this.$el.offset().left + widthDiff;
                        this.treeEl.offset(offset)
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
                console.log(boundingW, boundingH, scale)

                var l = this.$el.offset().left, t = this.$el.offset().top
                var w = this.$el.width(), h = this.$el.height()
                var box = [l + (100 - boundingW) * scale, t + (50 - boundingH) * scale, l + w - 100 * scale, t + h - 100 * scale]
                console.log(l, t)
                console.log(box)
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

                                            if (contextModel.get('page') == 'pathEditor') {
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
                                            if (contextModel.get('page') == 'pathEditor') {
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
                var old = curTree.get('selectedNodeOffset')
                if (old && selected.length && selected.is(':visible') && old.clickid == selected.attr('clickid')) {
                    var tree = this.treeEl.offset();
                    var cur = selected.offset();
                    this.treeEl.offset({left: tree.left - cur.left + old.left,
                        top: tree.top - cur.top + old.top});
                }

                contextModel.trigger('rendered')
                that.treeEl.css({'cursor': 'default'})


            },
            showExtraInfo: function () {

            },
            drawNodes: function () {


            },
            saveTreeFunction: function () {
                curTree.save()
            }
        })

        return TreeView
    });






