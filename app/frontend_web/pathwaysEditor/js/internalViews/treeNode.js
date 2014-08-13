define([
    // These are path alias that we configured in our main.js
    'jquery',     // lib/jquery/jquery
    'underscore', // lib/underscore/underscore
    'backbone',    // lib/backbone/backbone
    'models/contextModel',
    'modalViews/nodeEditor',
    'modalViews/protocolEditor',
    'models/nodeList',
    'models/nodeModel',
    'models/treeModel',

    'internalViews/protocolNode',
    'text!templates/treeNode.html'

    ], function($, _, Backbone, contextModel,  NodeEditor, ProtocolEditor, nodeList, nodeModel, curTree, ProtocolNode, nodeTemplate){

        var treeNode = Backbone.View.extend({

            template: _.template(nodeTemplate),
            initialize: function(params){
                this.childEntrances = []
                this.model = params.model
                if (params.el)
                    this.el = params.el
                this.$el.css({'float':'left'})
                var that = this;
                if(!(this.model.get('children').models)){
                    this.model.set('children', new nodeList(this.model.get('children')))
                    this.model.set({'hideChildren': "true"}, {silent: true})
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
            makeExit: function(){
                var exit = jsPlumb.addEndpoint(this.getMyElement(), {anchor: 'Bottom'})
                return exit
            },
            makeEntrance: function(){
                var entrance = jsPlumb.addEndpoint(this.getMyElement(), {anchor: 'Top'})
                return entrance
            },
            getMyElement: function(){
                return $('.treeNode', this.$el).first()

            },
            render: function(){
                this.$el.html(this.template(this.model.attributes))
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
                this.getMyElement().off('click')
                this.getMyElement().on('click', function(){
                    contextModel.set('selectedNode', that.model)

                })

                _.each(this.model.get('children').models, function(cur){
                    $('.children', this.$el).first().append("<div class='childSpot'></div>")
                    var targ = $('.childSpot',$('.children', this.$el).first()).last()
                    var thisChild = new treeNode({model: cur, el:targ})
                    curTree.elPairs.push({source: this, target: thisChild})


                }, this)
                if (this.model.get('hideChildren') == "true"){
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



                return this

            }




        })
        return treeNode;

    })

