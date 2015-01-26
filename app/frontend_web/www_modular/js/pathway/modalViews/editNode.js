/**
 * Created by Asmaa Aljuhani on 9/17/14.
 */
define([
    // These are path alias that we configured in our main.js
    'jquery',     // lib/jquery/jquery
    'underscore', // lib/underscore/underscore
    'backbone',    // lib/backbone/backbone
    'globalmodels/contextModel',
    'pathway/models/treeContext',
    'pathway/models/treeModel',
    'text!templates/pathway/NewNodeModal.html',
    'text!templates/pathway/NewProtocolModal.html',
    'singleRow/reminderRow',

], function ($, _, Backbone, contextModel, treeContext, curTree, nodeTemplate, protocolTemplate, ReminderRow) {
    var followups;

    var editNode = Backbone.View.extend({

        el: $("#modal-target"),
        initialize: function () {
            var that = this
           curTree.on('sync', function(){that.render()})
           this.render();
        },
        removeFollowupByValue: function(value){
            var newFollowups = new Array()
            for (var i in this.followups){
                var cur = this.followups[i]
                if (cur != value){
                    newFollowups.push(cur)
                }
            }
            this.followups = newFollowups



        },
        render: function(){
             //IF this is a protocol node, create a protocol node editor
            var that = this;
            if (treeContext.get('selectedNode').attributes.isProtocol) {
                this.template = _.template(protocolTemplate),
                    this.$el.html(this.template(treeContext.get('selectedNode').attributes));
                that.followups = new Array();

            if (typeof treeContext.get('selectedNode').attributes.followups != 'undefined') {
                $(treeContext.get('selectedNode').attributes.followups).each(function () {
                    //show all default followups
                    $('#followups', that.$el).append("<div class='followup'></div>");
                    var el = $('.followup', $('#followups', that.$el)).last();
                    var followup = new ReminderRow({model: new Backbone.Model(this), el: el, parent: that});

                    that.followups.push(followup);
                    followup.$el.bind('remove', {followup: followup}, that.removeFollowup);
                })
            }
                if ($('#addNodeButton').length) {
                $('#addNodeButton')[0].onclick = function () {
                    var protocolText = CKEDITOR.instances.ProtocolText.getData();
                    treeContext.get('selectedNode').set('protocol', protocolText);
                    treeContext.get('selectedNode').set('noteToCopy', $('#NoteToCopyText', this.$el).val());

                    var defaultRecipient = $("#defaultRecipient").val();
                    var defaultRecipientName = $("#defaultRecipientName").val();
                    var defaultQuickNote = $("#defaultQuickNote").val();
                    var followupRecipient = $("#defaultFollowupRecipient").val();
                    var followupRecipientName = $("#defaultFollowupRecipientName").val();
                    var followupInfo = [];

                    $(that.followups).each(function() {
                        //store all followups
                        var curFollowup = this.getCurrentParams();
                        if (!_.isEmpty(curFollowup)){
                            followupInfo.push(curFollowup);
                        }
                    });

                    treeContext.get('selectedNode').set('defaultRecipient', defaultRecipient);
                    treeContext.get('selectedNode').set('defaultRecipientName', defaultRecipientName);
                    treeContext.get('selectedNode').set('defaultQuickNote', defaultQuickNote);
                    treeContext.get('selectedNode').set('followups', followupInfo);
                    treeContext.get('selectedNode').set('defaultFollowupRecipient', followupRecipient);
                    treeContext.get('selectedNode').set('defaultFollowupRecipientName', followupRecipientName);

                    $('#detail-modal').modal('hide')
                    curTree.trigger('propagate')
                }}

                $("#detail-modal").modal({'show': 'true'});
                require(['ckeditor'], function() {
                    CKEDITOR.replace('ProtocolText');
                    CKEDITOR.instances.ProtocolText.setData(treeContext.get('selectedNode').get('protocol'));
                })
                $('#NoteToCopyText', this.$el).val(treeContext.get('selectedNode').get('noteToCopy'))

                $(".show-advanced-settings", this.$el).off('click');
            $(".show-advanced-settings", this.$el).on("click", function(event){
                if($(".advanced-settings", that.$el).is(":visible")){
                    $(event.target).switchClass("glyphicon-chevron-down","glyphicon-chevron-right", 0);
                    $(".advanced-settings", that.$el).slideUp(200);
                }
                else {
                    $(event.target).switchClass("glyphicon-chevron-right", "glyphicon-chevron-down", 0);
                    $(".advanced-settings").slideDown(200);
                }
            });

            $("#add-new-followup", this.$el).on("click", function() {
                $('#followups').append("<div class='followup'></div>"); //append(followup.render().el);
                var el = $('.followup', $('#followups')).last();
                var followup = new ReminderRow({model:new Backbone.Model({edit:true}), el:el});
                //followup.render();
                //followup.events();
                that.followups.push(followup);
                followup.$el.bind('remove', {followup:followup}, that.removeFollowup);
            });

            $('#defaultRecipient, #defaultFollowupRecipient', this.$el).autocomplete({
                source: function (request, response) {
                    $.ajax({
                        url: "/recipient",
                        term: request.term,
                        dataType: "json",
                        data: $.param(contextModel.toParams()) + "&target_user=" + request.term + "&target_role=provider",
                        success: function (data) {
                            response(data);
                        }
                    });
                },
                minLength: 3,
                select: function (event, ui) {
                    event.preventDefault();
                    $(event.target).parent().removeClass("has-error");
                    $("#addNodeButton", this.$el).removeAttr('disabled');
                    if(ui.item){
                        //fill in the autocomplete box with the display name and corresponding hidden input with the actual username
                        $(event.target).val(ui.item.label);
                        var nameInput = "#" + event.target.id + "Name";
                        $(nameInput).val(ui.item.value);
                    }
                    $(this).trigger('change');
                },
                change: function(event, ui) {
                    $(event.target).parent().removeClass("has-error");
                    $("#addNodeButton", this.$el).removeAttr('disabled');
                    if (!ui.item) {
                        //if the user does not select a recipient from the autocomplete
                        var nameInput = "#" + event.target.id + "Name";
                        $(nameInput).val("");

                        if ($(event.target).val() !== "") {
                            //cleared recipient
                            $(event.target).parent().addClass("has-error");
                            $("#addNodeButton", this.$el).prop("disabled",true)
                        }
                    }
                },
                autoFocus: true, //force the first value to be selected if user tabs away without selecting a recipient
                focus: function(event, ui){
                    //prevent the auto focus from changing the value of the text box
                    event.preventDefault();
                },
            });

             //IF this is an internal node, create an internal node editor
            } else {
                this.template = _.template(nodeTemplate),
                    this.$el.html(this.template(treeContext.get('selectedNode').attributes));
                $('#addNodeButton')[0].onclick = function () {
                    treeContext.get('selectedNode').set('name', $('#newNodeText', this.$el).val());
                    treeContext.get('selectedNode').set('tooltip', $('#newNodeTooltip', this.$el).val())
                    var data = CKEDITOR.instances.newNodeSideText.getData()
                    treeContext.get('selectedNode').set('sidePanelText', data)

                    $('#detail-modal').modal('hide')
                      curTree.trigger('propagate')
                }
                $("#detail-modal").modal({'show': 'true'});
                require(['ckeditor'], function() {
                    CKEDITOR.replace('newNodeSideText');
                })
            }




        },
        removeFollowup: function(event) {
            //remove reference to followup
            this.followups = _.without(followups, event.data.followup);
        }

    });
    return editNode
});
