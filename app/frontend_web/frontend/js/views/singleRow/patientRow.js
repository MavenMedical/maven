/***************************************************************************
 * Copyright (c) 2014 - Maven Medical
 * AUTHOR: 'Asmaa Aljuhani'
 * DESCRIPTION: This Javascript file handle a hierarchy of patientlist view
 *              so we can handle events easier.
 * LAST MODIFIED FOR JIRA ISSUE: MAV-97
 **************************************************************************/
define([
    // These are path alias that we configured in our main.js
    'jquery',     // lib/jquery/jquery
    'underscore', // lib/underscore/underscore
    'backbone',    // lib/backbone/backbone

    'currentContext',
    'eventhub',

    //Template
    'text!templates/templatesA/singleRow/patientRow.html'

], function ($, _, Backbone, currentContext, eventHub, patRowTemplate) {
    var patientRow = Backbone.View.extend({
        tagName: 'tr',
        template: _.template(patRowTemplate),
        events:{
            'click': 'handleClick'
        },
        render: function(){
            //add patient ids to currentContext patient array
            //currentContext.patients = currentContext.patients.concat((this.model.toJSON().id));
            console.log(currentContext);
            $(this.el).html(this.template(this.model.toJSON()));
            return this;
        },
        handleClick: function(){
            //update context
            currentContext.set({key : this.model.get("key")});
            currentContext.set({patients : this.model.get("id")});
	    currentContext.set({patientName : this.model.get("name")});
            console.log('I am here at patient row');
            eventHub.events.trigger('select:patient', 'test');
            //eventHub.events.on('selected:patient', console.log('patient selected') );


        }

    });

    return patientRow;

});