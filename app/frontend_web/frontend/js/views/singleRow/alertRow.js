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


    'views/widget/evidence',

    //Template
    'text!templates/singleRow/alertRow.html'

], function ($, _, Backbone, Evidence, alertRowTemplate) {
    var alertRow = Backbone.View.extend({
        tagName: 'div',
        template: _.template(alertRowTemplate),
        events:{
            'click .panel-heading': 'handleClick',
            'click span': 'showEvidence'
        },
        render: function(){
            $(this.el).html(this.template(this.model.toJSON()));
            return this;
        },
        showEvidence:function(){
            jQuery.noConflict();
            $('#evidence'+this.model.get('id')).modal();
        },
        handleClick: function(){
		var id = this.model.get('id');
		this.evidence = new Evidence({'evi': id});
		$('#collapse'+this.model.get('patient')+'-'+id).toggleClass("in");
        }

    });

    return alertRow;

});