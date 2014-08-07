define([
    // These are path alias that we configured in our main.js
    'jquery',     // lib/jquery/jquery
    'underscore', // lib/underscore/underscore
    'backbone',    // lib/backbone/backbone
    'modalViews/nodeEditor',
    'modalViews/protocolEditor',
    'models/nodeList',
    'models/nodeModel',
    'models/treeModel',

    'internalViews/protocolNode',
    'text!templates/treeNode.html'

    ], function($, _, Backbone,  NodeEditor, ProtocolEditor, nodeList, nodeModel, curTree, ProtocolNode, nodeTemplate){

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
                }
                var that = this
                this.model.get('children').off('add')
                this.model.get('children').on('add', function(){
                    curTree.trigger('propagate')
                },this)
                this.model.on('change', function(){
                    curTree.trigger('propagate')
                }, this)
                this.render()



            },
            makeExit: function(){
                var trueNode = $('.treeNode', this.$el).first()
                var exit = jsPlumb.addEndpoint(trueNode, {anchor: 'Bottom'})
                return exit
            },
            makeEntrance: function(){
                var trueNode = $('.treeNode', this.$el).first()
                var entrance = jsPlumb.addEndpoint(trueNode, {anchor: 'Top'})
                return entrance
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

                _.each(this.model.get('children').models, function(cur){
                    $('.children', this.$el).first().append("<div class='childSpot'></div>")
                    var targ = $('.childSpot',$('.children', this.$el).first()).last()
                    var thisChild = new treeNode({model: cur, el:targ})
                    curTree.elPairs.push({source: this, target: thisChild})


                }, this)

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

