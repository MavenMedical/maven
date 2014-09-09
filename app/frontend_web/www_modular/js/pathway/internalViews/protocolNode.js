define([
    // These are path alias that we configured in our main.js
    'jquery',     // lib/jquery/jquery
    'underscore', // lib/underscore/underscore
    'backbone',    // lib/backbone/backbone
    'globalmodels/contextModel',

    'text!templates/pathway/protocolNode.html',

], function ($, _, Backbone, currentContext, nodeTemplate) {

    var treeNode = Backbone.View.extend({

        template: _.template(nodeTemplate),
        events: {
            'click button#copybutton': 'copyProtocole'
        },
        initialize: function (params) {
            this.model = params.model
            this.$el.css({'float': 'left'})


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
                this.$el.html(this.template({protocolNode: this.model.get('protocol').attributes, page: currentContext.get('page')}));
            } else {
                this.$el.html(this.template({protocolNode: this.model.get('protocol'), page: currentContext.get('page')}));
            }

            return this
        },
        copyProtocole: function () {

            if (this.model.get('protocol').attributes) {
                console.log('copy text att', this.model.get('protocol').attributes.title)
                $('<div>'+this.model.get("protocol").title+'</div>').attr('id', 'copiedText').appendTo('.container');

            } else {
                console.log('copy text', this.model.get('protocol').title)
                $('<div>'+this.model.get("protocol").title+'</div>').attr('id', 'copiedText').appendTo('.container');

            }

            $('#toast').css('visibility', 'visible');

            setTimeout(function () {

                $("#toast").fadeOut("slow", function () {
                    //$('#toast').css('visibility', 'hidden');
                });

            }, 2000);

        },

        treeToJSON: function (node) {

        }





    })
    return treeNode;

})

