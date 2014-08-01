/***************************************************************************
 * Copyright (c) 2014 - Maven Medical
 * AUTHOR: 'Asmaa Aljuhani'
 * DESCRIPTION: This Javascript file handle a hierarchy of alerts view
 *              so we can handle events easier.
 * LAST MODIFIED FOR JIRA ISSUE: MAV-97
 **************************************************************************/
define([
    // These are path alias that we configured in our main.js
    'jquery',     // lib/jquery/jquery
    'underscore', // lib/underscore/underscore
    'backbone',    // lib/backbone/backbone

    'widgets/evidence',

    //Template
    'text!templates/alertRow.html',

    'globalmodels/contextModel'

], function ($, _, Backbone, Evidence, alertRowTemplate, contextModel) {

    showEvidence = function(evi) {
	var evidence = new Evidence({'evi':evi});
	$('#evidence-' + evi).modal();
    };


    var AlertRow = Backbone.View.extend({
        tagName: 'div',
        template: _.template(alertRowTemplate),
        events:{
            'click .panel-heading': 'handleClick',
            'click .like': 'like',
            'click .dislike': 'dislike',
            'click .dislike_info': 'critique',
            'click .dislike_text': 'clickText',
            'keyup .dislike_text':'doentercomment',
        },
        render: function(){
            $(this.el).html(this.template(this.model.toJSON()));
            return this;
        },
        like: function(){
            //user clicks 'like'
            this.rate("like");
        },
        dislike: function(){
            //user clicks 'dislike'
            $(this.el).find(".dislike_text").hide();
            this.rate("dislike");
        },
        rate: function(like){
            //sends like/dislike to backend
            that = this;
            $.ajax({
                url: "/rate_alert",
                data: $.param(contextModel.toParams()) + "&alert_id=" + that.model.get("id") +
                                                         "&category=" + that.model.get("alerttype") +
                                                         "&rule_id=" + that.model.get("ruleid") +
                                                         "&action="+like,
                success: function (data) {
                    console.log(data);
                }
            });
        },
        critique: function(event){
            //user gave additional info for 'dislike'
            that = this;
            var reason = $(event.target).attr("value");
            if (reason == "other")            {
                event.stopPropagation();
                if (!$(this.el).find(".dislike_text").is(":visible")) {
                    $(this.el).find(".dislike_text").show();
                }
                else{
                    $(this.el).find(".dislike_text").hide();
                }
            }
            else
            {
                $.ajax({
                    url: "/critique_alert",
                    data: $.param(contextModel.toParams()) + "&alert_id=" + that.model.get("id")+ "&rule_id=" + that.model.get("ruleid") +
                                                             "&category=" +that.model.get("alerttype") + "&action_comment="+reason,
                    success: function (data) {
                        console.log(data);
                    }
                });
            }
        },
        clickText: function(event){
            event.stopPropagation();
        },
        doentercomment: function(event){
	    if(event.keyCode == 13){
            event.preventDefault();
		    this.addComment();
	        }
	    },
        addComment: function(){
            var comment = $(this.el).find(".dislike_text_form").val();
            $(this.el).find(".dislike_text_form").val("");
            $(this.el).find(".dislike_text").hide();
            $(this.el).find(".dropdown-menu").trigger('click');
            console.log("Comment: " + comment);
             $.ajax({
                url: "/critique_alert",
                data: $.param(contextModel.toParams()) + "&rule_id=" + that.model.get("ruleid") + "&category=" +that.model.get("alerttype") + "&action_comment="+comment,
                success: function (data) {
                    console.log(data);
                }
            });
        },
        clickEvidenceSpan:function(){
            jQuery.noConflict();
	    this.evidence = new Evidence({'evi': this.model.get('ruleid')});
        },
        handleClick: function(){
		var id = this.model.get('id');
		$('#collapse'+this.model.get('patient')+'-'+id).toggleClass("in");
        }
    });

    return AlertRow;

});
