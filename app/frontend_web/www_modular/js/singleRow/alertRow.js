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
            'click .dislike_info': 'critique'
        },
        render: function(){
            $(this.el).html(this.template(this.model.toJSON()));
            return this;
        },
        like: function(){
            //user clicks 'like'
            console.log("Like clicked");
            this.rate("like");
        },
        dislike: function(){
            //user clicks 'dislike'
            console.log("Dislike clicked");
            this.rate("dislike");
        },
        rate: function(like){
            //sends like/dislike to backend
            $.ajax({
                url: "/rate_alert",
                data: $.param(contextModel.toParams()) + "&alert_id=" + this.model.get("id") +
                                                         "&category=" + this.model.get("alerttype") +
                                                         "&rule_id=" + this.model.get("ruleid") +
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
            $.ajax({
                url: "/critique_alert",
                data: $.param(contextModel.toParams()) + "&alert_id=" + that.model.get("id") +"&reason="+reason,
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
