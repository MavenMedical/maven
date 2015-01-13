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
        if (currentContext.get('page') != 'pathway' || treeContext.suppressClick || !currentContext.get('patients')) {
            return;
        }
        var target = $(evt.target).closest('.click-tracked')
        if (target.length) {
            var node_state = (target.attr('clickid'));
            var action_type = (target.attr('clickaction'));
            var details = target.attr('clickextra');
            if (!action_type) {
                if (target.is(':checkbox')) {
                    if (target.is(':checked')) {
                        action_type = 'checked'
                    } else {
                        action_type = 'unchecked'
                    }
                } else {
                    action_type = 'click'
                }
            }
            
            var data = {
                "patient_id": currentContext.get("patients"),
                "protocol_id": currentContext.get("pathid"),
                "node_state": node_state,
                "datetime": (new Date().toISOString()).replace("T", " "),
                "action": action_type,
                "details": details
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
            'click button#copybutton': 'copyProtocol',
            'click button#sendSetup-button': 'sendSetup',
            'click button#send-button': 'send',
            'click button#followup-button': 'followup',
            'click div.protocolNode': 'setSelectedNode'
        },
        initialize: function (params) {

            this.model = params.model
            this.hidden = params.hidden

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
            var that=this
            if (currentContext.get('patients') && !this.hidden) {
                $.ajax({
                    type: 'GET',
                    dataType: 'json',
                    url: "/node_activity",
                    data: decodeURIComponent($.param({
                        'protocol': curTree.get('pathid'),
                        'patient': currentContext.get("patients"),
                        'node_id': this.model.get('nodeID')
                    })),
                    success: function (data) {
                        var elem = $('input[type="checkbox"]', that.$el)
                        _.map(data, function(value, key) {
                            key = key.replace(/\s/g, '').toLowerCase()
                            var elem = $('input[clickextra="'+key+'"]', that.$el)
                            if (elem) {
                                elem.prop('checked', value=='checked')
                            }
                        })
                    }
                });
            }

            var protocolText = this.model.get('protocol')
            var re = /\[\[([\s\S]*?)\|([\s\S]*?)\]\]/g
                   
            var counts = {}
            protocolText = protocolText.replace(re, function(m, p1, p2) {
                key=p1.replace(/\s/g, '').toLowerCase()
		p2 = p2.split('<p>').join('').split('</p>').join('')
                if (counts[key] !== undefined) {
                    counts[key] += 1
                } else {
                    counts[key]=0
                }
                return '<input type="checkbox" value="'+p2+'" class="copy-text-button click-tracked" clickextra="' + key + '|' + counts[key] + '" clickid="TN-' + curTree.get('pathid') + '-' + that.model.get('nodeID')  + '"/> '+p1;
            })
            
            this.$el.html(this.template({pathID: curTree.get('pathid'), protocolNode: this.model.attributes, page: currentContext.get('page'),preview: currentContext.get('preview'),
                                         protocolText: protocolText}));
            $('.click-tracked input:checkbox', this.$el).click(function(evt) {activityTrack(evt)})
            $('.copy-text-button', this.$el).click(function(evt) {evt.stopPropagation()})
            if (this.model == treeContext.get('selectedNode')){
                $('.protocolNode', this.$el).addClass("selected")
            }
            return this
        },
        copyProtocol: function (evt) {
            evt.stopPropagation()
            activityTrack(evt)

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
            activityTrack(evt)
            var newSendProtocol = new SendProtocol(this.model);
        },
        followup: function (evt) {
            evt.stopPropagation()
            activityTrack(evt)
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

