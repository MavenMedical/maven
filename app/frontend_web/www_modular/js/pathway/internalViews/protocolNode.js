define([
    // These are path alias that we configured in our main.js
    'jquery',     // lib/jquery/jquery
    'underscore', // lib/underscore/underscore
    'backbone',    // lib/backbone/backbone
    'globalmodels/contextModel',
    'pathway/models/treeModel',
    'pathway/models/treeContext',
    'pathway/modalViews/sendProtocol',
    'pathway/modalViews/sendFollowups',
    'text!templates/pathway/protocolNode.html'

], function ($, _, Backbone, currentContext, curTree, treeContext , SendProtocol, SendFollowups, nodeTemplate) {

    var activityTrack = function (evt) {
        //Don't track clicks in edit mode (where page would be "pathwayEditor")
        if (currentContext.get('page') != 'pathway' || treeContext.suppressClick) {
            return;
        }
        var target = $(evt.target)
        console.log(target.closest('.click-tracked'))
        if (target.closest('.click-tracked').length) {
            var node_state = (target.closest('.click-tracked').attr('clickid'));

            var data = {
                "patient_id": currentContext.get("patients"),
                "protocol_id": currentContext.get("pathid"),
                "node_state": node_state,
                "datetime": (new Date().toISOString()).replace("T", " "),
                "action": "click"
            }
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
    }
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



            setSelectedNode: function(evt){
                if (treeContext.suppressClick) {
                    return
                }
                activityTrack(evt);
                this.getMyElement().off('click');
                treeContext.set('selectedNode', this.model, {silent: true});
                treeContext.trigger('propagate')
            },


        render: function () {
            var protocolText = this.model.get('protocol')
            var re = /\[\[([\s\S]*?)\|([\s\S]*?)\]\]/g
            protocolText = protocolText.replace(re, function(m, p1, p2) {
		p2 = p2.split('<p>').join('').split('</p>').join('')
                return '<input type="checkbox" value="'+p2+'" class="copy-text-button"/> '+p1;
            })
            
            this.$el.html(this.template({pathID: curTree.get('pathid'), protocolNode: this.model.attributes, page: currentContext.get('page'),
                                         protocolText: protocolText}));
            $('.copy-text-button', this.$el).click(function(evt) {evt.stopPropagation()})
            if (this.model == treeContext.get('selectedNode')){
                $('.protocolNode', this.$el).addClass("selected")
            }
            return this
        },
        copyProtocole: function (evt) {
            evt.stopPropagation()


            $('#copiedText').remove();

             //this.trackActivity("copytext");
            var copytext = this.model.get('noteToCopy')
            $('input:checked', this.$el).each(function(index, elem) {
                copytext = copytext + "  \n\n" + elem.value
            })


            $('<div>'+copytext+'</div>').attr('id', 'copiedText').appendTo('body');


           //toast code
            $('#toast').empty()
            $('<span class="glyphicon glyphicon-ok"></span><span>Note-ready text added to clipboard</span>').appendTo('#toast')
            //$('#toast').innerHTML = 'Note-ready text added to clipboard'



            $('#toast').css('top', $('#copybutton').offset().top + 30)
            $('#toast').css('left', $('#copybutton').offset().left )

            $('#toast').css('visibility', 'visible');


            setTimeout(function () {

               // $("#toast").fadeOut("slow", function () {
                    $('#toast').css('visibility', 'hidden');
               // });

            }, 1500);

        },
        send: function (evt) {
            evt.stopPropagation()
            var newSendProtocol = new SendProtocol(this.model);
        },
        followup: function (evt) {
            evt.stopPropagation()
            var sendFollowups = new SendFollowups(this.model);
        },
        sendSetup: function (evt) {
            evt.stopPropagation()

        },
        getMyElement: function(){
                return $('.protocolNode', this.$el).first()

        },
	childrenHidden: function() {return false;},
	hideChildren: function() {},
	showChildren: function() {}

    })
    protocolNode.activityTrack = activityTrack
    return protocolNode

})

