/***************************************************************************
 * Copyright (c) 2014 - Maven Medical
 * AUTHOR: 'Asmaa Aljuhani'
 * DESCRIPTION: This is an instance from the Hub Event backbone class.
 *              This eventhub will be used in all views. Passing an instance
 *              from a model make this object global, so all views can
 *              trigger and listen to events.
 * PREREQUISITE: libraries should be predefine in main.js
 * LAST MODIFIED FOR JIRA ISSUE: MAV-98
 **************************************************************************/
define([
    'jquery',     // lib/jquery/jquery
    'underscore', // lib/underscore/underscore
    'backbone',    // lib/backbone/backbone
    'events/hub'

], function ($, _, Backbone,Hub) {
    var eventHub = new Hub();

    /*
    This is a sample code of how you can trigger an event
    and how to listen to it.
      eventHub.events.on("change:user", something.update);
      eventHub.events.trigger('change: user', 'hello');
     */

    return eventHub;

});

