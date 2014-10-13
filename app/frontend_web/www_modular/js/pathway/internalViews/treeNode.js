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

    'pathway/internalViews/protocolNode',
    'text!templates/pathway/treeNode.html'

    ], function($, _, Backbone, currentContext,  NodeEditor, ProtocolEditor, nodeList, nodeModel, curTree, ProtocolNode, nodeTemplate){

        var treeNode = Backbone.View.extend({

            template: _.template(nodeTemplate),
            initialize: function(params){
                this.childEntrances = []
                this.model = params.model
                if (params.el)
                    this.el = params.el
                this.$el.css({'float':'left'})
                var that = this;
                if (!this.model.get('children')){
                    return;
                } else
                if(!(this.model.get('children').models)){
                    this.model.set('children', new nodeList(this.model.get('children')), {silent: true})
                }
                var that = this
                this.model.get('children').off('add')
                this.model.get('children').on('add', function(){
                    curTree.trigger('propagate')
                },this)
                this.model.off('change')
                this.model.on('change', function(){
                    curTree.trigger('propagate')
                }, this)
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
            getMyElement: function(){
                return $('.treeNode', this.$el).first()

            },
            render: function(){
                if (!this.model.get('hideChildren')){
                    this.model.set('hideChildren', false, {silent: true})
                }
                this.$el.html(this.template({treeNode: this.model.attributes, page: currentContext.get('page'), pathid: curTree.get('id')}));
                var that = this;

                //Set on clicks
                $('.collapseButton', this.$el).first().off('click')
                $('.collapseButton', this.$el).first().on('click', function(){
                       if (currentContext.get('page')=='pathEditor'){
                           if (that.model.get('hideChildren') == "false"){
                               curTree.collapse(that.model)
                           } else{
                               that.model.set('hideChildren', "false")
                           }
                           curTree.getShareCode()


                       }
                })
                $("#addChildButton", this.$el).off('click')
                $("#addChildButton", this.$el).on('click', function(){
                     var newEditor = new NodeEditor(that.model)
                })
                $(".addProtocolButton", this.$el).on('click', function(){
                     var newEditor = new ProtocolEditor(that.model)
                })
                this.getMyElement().off('click')
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

                    }
                    curTree.trigger('propagate')

                })

                _.each(this.model.get('children').models, function(cur){
                    $('.children2', this.$el).first().append("<div class='childSpot'></div>")
                    var targ = $('.childSpot',$('.children2', this.$el).first()).last()
                    var thisChild = new treeNode({model: cur, el:targ})
                    var n =  ((cur.get('hideChildren') == "false") || cur == curTree.get('selectedNode')  )
                    curTree.elPairs.push({source: this, target: thisChild, bold: n})
                }, this)
                if (this.model.get('hideChildren') == "true"){
                    $('.children2', this.$el).first()[0].hidden = true;
                } else {
                    $('.children2', this.$el).first()[0].hidden = false;

                }

                if (this.model == curTree.get('selectedNode')){
                    that.getMyElement().addClass('selected')
                }

                if (this.model.get('protocol')){
                    var protoNode = new ProtocolNode({model: this.model})
                    $('.protocol', this.$el).first().append(protoNode.render().$el)
                    curTree.elPairs.push({source: this, target: protoNode, bold: true})
                    $('.removeProtocolButton', this.$el).on("click", function(){
                        that.model.unset('protocol')
                    })

                }



                return this

            }




        })
        return treeNode;

    })

