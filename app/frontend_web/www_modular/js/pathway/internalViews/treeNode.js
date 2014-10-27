define([
    // These are path alias that we configured in our main.js
    'jquery',     // lib/jquery/jquery
    'underscore', // lib/underscore/underscore
    'backbone',    // lib/backbone/backbone
    'globalmodels/contextModel',
    'pathway/modalViews/nodeEditor',
    'pathway/modalViews/protocolEditor',
    'pathway/models/nodeList',
    'pathway/models/nodeModel',
    'pathway/models/treeModel',

    'text!templates/pathway/treeNode.html'

    ], function($, _, Backbone, currentContext,  NodeEditor, ProtocolEditor, nodeList, nodeModel, curTree, nodeTemplate){

        var treeNode = Backbone.View.extend({
            nodeType: "standard",

            template: _.template(nodeTemplate),
            initialize: function(params){
                this.childEntrances = []
                this.model = params.model
                if (params.el)
                    this.el = params.el
                this.$el.css({'float':'left'})
                var that = this;

                    this.render()

            },
            makeExit: function(jsPlumb2){
                var exit = jsPlumb2.addEndpoint(this.getMyElement(), {anchor: 'Bottom'})
                return exit
            },
            makeEntrance: function(jsPlumb2){
                var entrance = jsPlumb2.addEndpoint(this.getMyElement(), {anchor: 'Top'})
                return entrance
            },



            setSelectedNode: function(){
                this.getMyElement().off('click');
                curTree.set('selectedNode', this.model, {silent: true});
                curTree.trigger('propagate')
            },

            getMyElement: function(){
                return $('.treeNode', this.$el).first()

            },
            render: function(){
                if (!this.model.get('hideChildren')){
                    this.model.set('hideChildren', false, {silent: true})
                }
                this.$el.html(this.template({node: this.model.attributes, page: currentContext.get('page'), pathid: curTree.get('id')}));
                var that = this;

                //Set on clicks
                $('.collapseButton', this.$el).first().on('click', function(){
                       if (currentContext.get('page')=='pathEditor'){
                           if (that.model.get('hideChildren') == "false"){
                               curTree.collapse(that.model)
                           } else{
                               that.model.set('hideChildren', "false", {silent: true})
                           }
                           curTree.getShareCode()
                       }
                })
                $("#addChildButton", this.$el).first().on('click', function(){
                     var newEditor = new NodeEditor(that.model)
                })
                $("#moveLeftButton", this.$el).on('click', function(){
                     curTree.changeNodePosition(that.model, -1)
                })
                $("#moveRightButton", this.$el).first().on('click', function(){
                     curTree.changeNodePosition(that.model, 1)
                })
                $(".addProtocolButton", this.$el).first().on('click', function(){
                     var newEditor = new ProtocolEditor(that.model)
                })
                this.getMyElement().on('click', function(){
                    curTree.set('selectedNode', that.model, {silent: true})
                    if (currentContext.get('page')!='pathEditor'){
                       if (that.model.get('hideChildren') == "false"){
                           curTree.collapse(that.model)
                       } else{
                            curTree.hideSiblings(that.model)
                            that.model.set('hideChildren', "false", {silent: true})
                       }
                       curTree.getShareCode()
                    } else {
                        curTree.trigger('propagate')
                    }

                })

                _.each(this.model.get('children').models, function(cur){
                    if (!cur.get('isProtocol')){
                        $('.children2', this.$el).first().append("<div class='childSpot'></div>")
                        var targ = $('.childSpot',$('.children2', this.$el).first()).last()
                        cur.set('hasLeft',(this.model.get('children').indexOf(cur) != 0))
                        cur.set('hasRight', (this.model.get('children').indexOf(cur) < this.model.get('children').length - 1))

                        var thisChild = new treeNode({model: cur, el:targ})

                        var n =  ((cur.get('hideChildren') == "false") || cur == curTree.get('selectedNode')  )
                        curTree.elPairs.push({source: this, target: thisChild, bold: n})
                    } else {
                       that.addProtocol(cur)
                    }

                }, this)


                if (this.model.get('hideChildren') == "true" && this.nodeType=="standard"){
                    $('.children2', this.$el).first().css({'display':'none'});
                } else {
                    $('.children2', this.$el).first().css({'display':'block'});

                }

                if (this.model == curTree.get('selectedNode')){
                    that.getMyElement().addClass('selected')
                }





                return this

            },
            addProtocol: function(protoModel){
                 var that = this
                    require(['pathway/internalViews/protocolNode',], function(ProtocolNode){
                        console.log('the protocol node', ProtocolNode)
                        var protoNode = new ProtocolNode({model: protoModel})
                        $('.protocol', that.$el).first().append(protoNode.render().$el)
                        curTree.elPairs.push({source: that, target: protoNode, bold: true})
                        $('.removeProtocolButton', that.$el).on("click", function(){
                            curTree.deleteNode(protoModel, false)
                        })
                        curTree.trigger('drawJSPlumb')

                    })
            }




        })
        return treeNode;

    })

