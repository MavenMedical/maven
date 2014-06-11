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
    'text!templates/alertRow.html'

], function ($, _, Backbone, Evidence, alertRowTemplate) {

    showEvidence = function(evi) {
	var evidence = new Evidence({'evi':evi});
	$('#evidence-' + evi).modal();
    };


    var AlertRow = Backbone.View.extend({
        tagName: 'div',
        template: _.template(alertRowTemplate),
        events:{
            'click .panel-heading': 'handleClick',
        },
        render: function(){
            $(this.el).html(this.template(this.model.toJSON()));
            return this;
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
