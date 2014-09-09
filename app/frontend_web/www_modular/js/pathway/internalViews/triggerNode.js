define([
    // These are path alias that we configured in our main.js
    'jquery',     // lib/jquery/jquery
    'underscore', // lib/underscore/underscore
    'backbone',    // lib/backbone/backbone
    'pathway/modalViews/nodeEditor',
    'pathway/modalViews/protocolEditor',
    'pathway/modalViews/detailEditor',
   'globalmodels/contextModel',
    'pathway/models/nodeList',
    'pathway/models/nodeModel',
    'pathway/models/treeModel',
    'pathway/internalViews/protocolNode',
    'pathway/internalViews/treeNode',
    'text!templates/pathway/triggerNode.html',
    'text!templates/pathway/triggerRow.html'

    ], function($, _, Backbone,  NodeEditor, ProtocolEditor, DetailEditor, currentContext,  nodeList, nodeModel, curTree, ProtocolNode, TreeNode, nodeTemplate, rowTemplate){

        var TriggerNode = TreeNode.extend({

            template: _.template(nodeTemplate),
            initialize: function(params){
                this.model = params.model
                if (params.el)
                    this.el = params.el
                this.$el.css({'float':'left'})

                var that = this;
                if(!(this.model.get('children').models)){
                    this.model.set('children', new nodeList(this.model.get('children')))
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
                this.model.get('triggers').off('add')
                this.model.get('triggers').on('add', function(){
                    curTree.trigger('propagate')
                },this)
                this.model.get('triggers').off('remove')
                this.model.get('triggers').on('remove', function(){
                    curTree.trigger('propagate')
                },this)
                this.render()


            },
            makeExit: function(jsPlumb2){

                this.exit = jsPlumb2.addEndpoint(this.getMyElement(), {anchor: 'Bottom'})

                return this.exit
            },
            makeEntrance: function(jsPlumb2){
                this.entrance = jsPlumb2.addEndpoint(this.getMyElement(), {anchor: 'Top'})
                return this.entrance
            },
            getMyElement: function(){
                    return $('.treeNode', this.$el).first()
            },
            render: function(){
                 if (!this.model.get('hideChildren')){
                    this.model.set('hideChildren', false, {silent: true})
                }
                this.$el.html(this.template({triggerNode: this.model.attributes, page: currentContext.get('page')}))

                  var that = this;

                //Set on clicks
                $('.collapseButton', this.$el).first().off('click')
                $('.collapseButton', this.$el).first().on('click', function(){
                       if (that.model.get('hideChildren') == "false"){
                           that.model.set('hideChildren', "true")
                       } else{
                            that.model.set('hideChildren', "false")
                       }
                })

                $("#addChildButton", this.$el).off('click')
                $("#addChildButton", this.$el).on('click', function(){
                     var newEditor = new NodeEditor(that.model)
                })
                $(".addProtocolButton", this.$el).on('click', function(){
                     var newEditor = new ProtocolEditor(that.model)
                })
                $("#addTriggerButton", this.$el).on('click', function(){
                     var newEditor = new DetailEditor({triggerNode: that.model})
                     newEditor.render()
                })

                this.getMyElement().off('click')
                this.getMyElement().on('click', function(){
                    curTree.set('selectedNode', that.model, {silent: true})
                    curTree.trigger('propagate')
                })
                _.each(this.model.get('children').models, function(cur){

                    $('.children2', this.$el).first().append("<div class='childSpot'></div>")
                    var targ = $('.childSpot',$('.children2', this.$el).first()).last()
                    var thisChild = new TreeNode({model: cur, el:targ})
                    curTree.elPairs.push({source: this, target: thisChild})
                }, this)

                if (this.model.get('hideChildren')=="true"){
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
                    curTree.elPairs.push({source: this, target: protoNode})
                    $('.removeProtocolButton', this.$el).on("click", function(){
                        that.model.unset('protocol')
                    })

                }
                if (this.model.get('triggers')){
                    var triggerEl = $('.triggerView', this.$el)
                    var rowTemp = _.template(rowTemplate)
                    triggerEl.html("");
                    _.each(this.model.get('triggers').models, function(cur){
                        triggerEl.append(rowTemp(cur.attributes))
                        var that = this
                        var curRemoveButton = $('.remove-detail', triggerEl).last()
                        curRemoveButton.on('click', function(){
                            that.model.get('triggers').remove(cur)
                        })

                    }, this)

                }

                return this

            }
        })

        return TriggerNode;

    })

