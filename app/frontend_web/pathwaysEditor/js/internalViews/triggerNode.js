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
    'internalViews/protocolNode',
    'internalViews/treeNode',
    'text!templates/triggerNode.html'

    ], function($, _, Backbone,  NodeEditor, ProtocolEditor, DetailEditor, nodeList, nodeModel, ProtocolNode, TreeNode, nodeTemplate){

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

                this.model.get('children').on('add', this.render,this)
                this.model.on('change', this.render, this)

                this.render()


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
                $('.children', this.$el).html("")
                _.each(this.model.get('children').models, function(cur){
                    $('.children', this.$el).first().append(new TreeNode({model: cur}).render().$el)
                }, this)

                if (this.model.get('protocol')){
                    $('.protocol', this.$el).first().append(new ProtocolNode({model: this.model}).render().$el)
                    $('.removeProtocolButton', this.$el).on("click", function(){
                        that.model.unset('protocol')
                    })

                }
                return this

            }
        })

        return TriggerNode;

    })

