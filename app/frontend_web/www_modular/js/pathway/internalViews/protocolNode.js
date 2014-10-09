define([
    // These are path alias that we configured in our main.js
    'jquery',     // lib/jquery/jquery
    'underscore', // lib/underscore/underscore
    'backbone',    // lib/backbone/backbone
    'globalmodels/contextModel',
    'pathway/models/treeModel',
    'pathway/modalViews/sendProtocol',
    'text!templates/pathway/protocolNode.html',

], function ($, _, Backbone, currentContext, curTree, SendProtocol, nodeTemplate) {

    var treeNode = Backbone.View.extend({

        template: _.template(nodeTemplate),
        events: {
            'click button#copybutton': 'copyProtocole',
            'click button#sendSetup-button': 'sendSetup',
            'click button#send-button': 'send',
            'click div.protocolNode': 'setSelectedNode'
        },
        initialize: function (params) {
            this.model = params.model

        },
        makeExit: function (jsPlumb2) {

            var exit = jsPlumb2.addEndpoint(this.$el, {anchor: 'Bottom'})
            return exit
        },
        makeEntrance: function (jsPlumb2) {

            var entrance = jsPlumb2.addEndpoint(this.$el, {anchor: 'Top'})
            return entrance
        },
        render: function () {
            if (this.model.get('protocol').attributes) {
                console.log(this.model.get('protocol').attributes)
                this.$el.html(this.template({protocolNode: this.model.get('protocol').attributes, page: currentContext.get('page')}));
            } else {
                                console.log("PROTO", this.model.get('protocol'))
                this.$el.html(this.template({protocolNode: this.model.get('protocol'), page: currentContext.get('page')}));
            }

            return this
        },
        copyProtocole: function () {

             this.trackActivity("copytext");

             console.log('copy text', this.model.get('protocol').noteToCopy)
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
        sendSetup: function () {


        },
        setSelectedNode: function(){
                this.$el.off('click')
                this.trackActivity("click");

                    curTree.set('selectedNode', this.model.get('protocol'), {silent: true})
                    curTree.trigger('propagate')
        },
        treeToJSON: function (node) {

        },
        trackActivity: function (action){
            var id = 0; //no valid id now: wait until protocol nodes have their own id

                            var data = { "patient_id": currentContext.get("patients"),
                                         "protocol_id": currentContext.get("pathid"),
                                         "node_id": id,
                                         "datetime": (new Date().toISOString()).replace("T"," "),
                                         "action": action }
            $.ajax({
                type: 'POST',
                dataType: 'json',
                url: "/activity?" + $.param(currentContext.toParams()),
                data: JSON.stringify(data),
                success: function () {
                    console.log("click tracked");
                }
            });
        }
    })
    return treeNode;

})

