define([
    // These are path alias that we configured in our main.js
    'jquery',     // lib/jquery/jquery
    'underscore', // lib/underscore/underscore
    'backbone',    // lib/backbone/backbone
    'globalmodels/contextModel',

    'pathway/internalViews/protocolNode',
    'pathway/modalViews/nodeEditor',
    'pathway/modalViews/protocolEditor',
    'pathway/models/nodeModel',
    'pathway/models/treeModel',
    'pathway/models/treeContext',
    'text!templates/pathway/treeNode.html'

], function ($, _, Backbone, currentContext, ProtocolNode, NodeEditor, ProtocolEditor, nodeModel, curTree, treeContext, nodeTemplate) {
        //the backbone view for rendering a node of the tree, this is a recursive view which contains tree views for
        //all of its children
    var treeNode = Backbone.View.extend({
        nodeType: "standard",

        template: _.template(nodeTemplate),
        initialize: function (params) {
            //child entrances keeps track of the endpoints where we need to attach jsplumb
            this.childEntrances = []

            this.model = params.model
            if (params.el)
                this.el = params.el
            this.$el.css({'float': 'left'})
            var that = this;

            this.render()

        },
        //create JSPlumb endpoints for the entrance and exits of the node

        makeExit: function (jsPlumb2) {
            var exit = jsPlumb2.addEndpoint(this.getMyElement(), {anchor: 'Bottom'})
            return exit
        },
        makeEntrance: function (jsPlumb2) {
            var entrance = jsPlumb2.addEndpoint(this.getMyElement(), {anchor: 'Top'})
            return entrance
        },

        //this function is called by clicking the node and sets the node's internal model to be the selected
        //node in the treeContext
        setSelectedNode: function () {
            if (treeContext.suppressClick) {
                return
            }
            this.getMyElement().off('click');
             if (treeContext.get('selectedNode')!= this.model){
                   treeContext.set('selectedNode', this.model, {silent: true});
                   treeContext.trigger('propagate')
                }
        },
        //function to return the el corresponding to the actual visible region of the tree node which indicate this
        //node (the entire element also contains the children)
        getMyElement: function () {
            return $('.treeNode', this.$el).first()

        },
        render: function () {
            this.$el.html(this.template({
                node: this.model.attributes,
                childrenHidden: this.model.childrenHidden(),
                page: currentContext.get('page'),
                pathid: curTree.get('pathid'),
                preview: currentContext.get('preview')
            }));
            var that = this;

            //Set on clicks

            $('.collapseButton', this.$el).first().on('click', function () {
                if (treeContext.suppressClick) {
                    return
                }
                if (currentContext.get('page') == 'pathEditor' ) {
                    if (!that.model.childrenHidden()) {
                        curTree.collapse(that.model)
                    } else {
                        that.model.showChildren()
                    }
                    //the cur tree needs to get the new accurate path state code and set it in the url
                    curTree.getShareCode()
                }
            })

            $("#addChildButton", this.$el).first().on('click', function () {
                var newEditor = new NodeEditor(that.model)
            })
            $("#moveLeftButton", this.$el).on('click', function () {
                curTree.changeNodePosition(that.model, -1)
            })
            $("#moveRightButton", this.$el).first().on('click', function () {
                treeContext.unset('selectedNodeOffset');
                curTree.changeNodePosition(that.model, 1)
            })
            $(".addProtocolButton", this.$el).first().on('click', function () {
                var newEditor = new ProtocolEditor(that.model)
            })
            this.getMyElement().on('click', function (evt) {
                if (treeContext.suppressClick) {
                    return
                }
                //activity tracking
                ProtocolNode.activityTrack(evt);
                var selected = $(evt.currentTarget)
                var offset = selected.offset();
                offset.clickid = selected.attr('clickid');
                treeContext.set({
                    'selectedNodeWidth': selected.outerWidth(), 'selectedNodeOffset': offset,
                    'selectedNode': that.model
                }, {silent: true})
                if (currentContext.get('page') != 'pathEditor' || currentContext.get('preview')) {
                    if (!that.model.childrenHidden()) {
                        curTree.collapse(that.model)
                    } else {
                        curTree.hideSiblings(that.model)
                        that.model.showChildren()
                    }
                    //the cur tree needs to get the new accurate path state code, and set it in the url
                    curTree.getShareCode()
                } else {

                    treeContext.trigger('propagate')
                }

            })
            //for each child of this node
            _.each(this.model.get('children').models, function (cur) {
                //if this is not a protocol
                if (!cur.get('isProtocol')) {

                    //create a new child spot in this nodes childrens section
                    $('.children2', this.$el).first().append("<div class='childSpot'></div>")

                    var targ = $('.childSpot', $('.children2', this.$el).first()).last()
                    //set the new child node's temp variables based on whether or not it needs a right and or left arrow
                    cur.set('hasLeft', (this.model.get('children').indexOf(cur) != 0))
                    cur.set('hasRight', (this.model.get('children').indexOf(cur) < this.model.get('children').length - 1))
                    //create a new tree node in the new spot with the current model
                    var thisChild = new treeNode({model: cur, el: targ})
                    //set the nodes child visiblity
                    var n = (!cur.childrenHidden() || cur == treeContext.get('selectedNode')  )
                    //add to the list of jsplumb's to draw a connection between this node and the child, bolded if it
                    //is on the path to the selected node
                    curTree.elPairs.push({source: this, target: thisChild, bold: n})
                } else {
                    //otherwise just make a protocol node and let the add protocol method handle it
                    that.addProtocol(cur)
                }

            }, this)

            //show or hide this nodes children based on the temp variable in its model
            if (this.model.childrenHidden() && this.nodeType == "standard") {
                $('.children2', this.$el).first().css({'display': 'none'});
            } else {
                $('.children2', this.$el).first().css({'display': 'block'});

            }
            //highlight this node if it is the selected node
            if (this.model == treeContext.get('selectedNode')) {
                that.getMyElement().addClass('selected')
            }


            return this

        },

        //the add protocol method, handles painting a protocol as a child of this node
        addProtocol: function (protoModel) {
            var that = this
            var protoNode = new ProtocolNode({model: protoModel, hidden: this.model.childrenHidden()})
            $('.protocol', that.$el).first().append(protoNode.render().$el)
            curTree.elPairs.push({source: that, target: protoNode, bold: true})
            $('.removeProtocolButton', that.$el).on("click", function () {
                curTree.deleteNode(protoModel, false)
            })

        }
    })
    return treeNode;
})

