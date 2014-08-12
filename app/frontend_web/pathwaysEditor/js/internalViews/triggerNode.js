define([
    // These are path alias that we configured in our main.js
    'jquery',     // lib/jquery/jquery
    'underscore', // lib/underscore/underscore
    'backbone',    // lib/backbone/backbone
    'modalViews/nodeEditor',
    'modalViews/protocolEditor',
    'modalViews/detailEditor',

    'models/nodeList',
    'models/nodeModel',
    'models/treeModel',
    'internalViews/protocolNode',
    'internalViews/treeNode',
    'text!templates/triggerNode.html',
    'text!templates/triggerRow.html'

    ], function($, _, Backbone,  NodeEditor, ProtocolEditor, DetailEditor, nodeList, nodeModel, curTree, ProtocolNode, TreeNode, nodeTemplate, rowTemplate){

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
            makeExit: function(){

                var trueNode = $('.treeNode', this.$el).first()
                this.exit = jsPlumb.addEndpoint(trueNode, {anchor: 'Bottom'})

                return this.exit
            },
            makeEntrance: function(){
                var trueNode = $('.treeNode', this.$el).first()
                this.entrance = jsPlumb.addEndpoint(trueNode, {anchor: 'Top'})
                return this.entrance
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

                _.each(this.model.get('children').models, function(cur){


                    $('.children', this.$el).first().append("<div class='childSpot'></div>")
                    var targ = $('.childSpot',$('.children', this.$el).first()).last()
                    var thisChild = new TreeNode({model: cur, el:targ})
                    curTree.elPairs.push({source: this, target: thisChild})




                }, this)

                if (this.model.get('hideChildren')=="true"){
                    $('.children', this.$el).first()[0].hidden = true;
                } else {
                    $('.children', this.$el).first()[0].hidden = false;
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

