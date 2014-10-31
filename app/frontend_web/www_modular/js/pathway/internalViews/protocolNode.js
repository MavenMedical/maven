define([
    // These are path alias that we configured in our main.js
    'jquery',     // lib/jquery/jquery
    'underscore', // lib/underscore/underscore
    'backbone',    // lib/backbone/backbone
    'globalmodels/contextModel',
    'pathway/internalViews/treeNode',
    'pathway/models/treeModel',
    'pathway/modalViews/sendProtocol',
    'pathway/modalViews/sendFollowups',
    'text!templates/pathway/protocolNode.html',

], function ($, _, Backbone, currentContext, treeNode, curTree, SendProtocol, SendFollowups, nodeTemplate) {

    var protocolNode = Backbone.View.extend({


        nodeType: "protocol",
        template: _.template(nodeTemplate),
        events: {
            'click button#copybutton': 'copyProtocole',
            'click button#sendSetup-button': 'sendSetup',
            'click button#send-button': 'send',
            'click button#followup-button': 'followup',
            'click div.protocolNode': 'setSelectedNode'
        },
        initialize: function (params) {

            this.model = params.model

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


        render: function () {
            if (this.model.get('protocol') && this.model.get('protocol').attributes) {
                this.$el.html(this.template({pathID: curTree.get('id'), protocolNode: this.model.attributes, page: currentContext.get('page')}));
            } else {
                this.$el.html(this.template({pathID: curTree.get('id'), protocolNode: this.model.attributes, page: currentContext.get('page')}));
            }
            if (this.model == curTree.get('selectedNode')){
                $('.protocolNode', this.$el).addClass("selected")
            }
            return this
        },
        copyProtocole: function () {

             this.trackActivity("copytext");

             $('<div>'+this.model.get("protocol").noteToCopy+'</div>').attr('id', 'copiedText').appendTo('.container');

            $('#toast').css('visibility', 'visible');

            setTimeout(function () {

                $("#toast").fadeOut("slow", function () {
                    //$('#toast').css('visibility', 'hidden');
                });

            }, 2000);

        },
        send: function () {
            var newSendProtocol = new SendProtocol(this.model);
        },
        followup: function () {
            var sendFollowups = new SendFollowups(this.model);
        },
        sendSetup: function () {


        },
        getMyElement: function(){
                return $('.protocolNode', this.$el).first()

        }

    })
    return protocolNode;

})

