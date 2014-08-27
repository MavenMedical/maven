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

    ], function($, _, Backbone,  NodeEditor, ProtocolEditor, DetailEditor, contextModel,  nodeList, nodeModel, curTree, ProtocolNode, TreeNode, nodeTemplate, rowTemplate){

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
                this.model.on('change', function(){
                    curTree.trigger('propagate')
                }, this)
                this.model.get('triggers').off('add')
                this.model.get('triggers').on('add', function(){
                    curTree.trigger('propagate')
                },this)
                this.model.get('triggers').on('remove', function(){
                    curTree.trigger('propagate')
                },this)
                this.render()


            },
            makeExit: function(jsPlumb2){

                this.exit = jsPlumb2.addEndpoint(this.getMyElement(), {anchor: 'Bottom'})
                                console.log(jsPlumb2)

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
                this.$el.html(this.template({protocol: this.model.get('protocol'), children: this.model.get('children'), text: this.model.get('text')}))

                  var that = this;
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
                    contextModel.set('selectedNode', that.model)
                })
                _.each(this.model.get('children').models, function(cur){

                    console.log('lets render', cur)
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
                if (this.model == contextModel.get('selectedNode')){
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

