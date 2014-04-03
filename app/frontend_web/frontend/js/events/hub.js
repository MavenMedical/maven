/***************************************************************************
 * Copyright (c) 2014 - Maven Medical
 * AUTHOR: 'Asmaa Aljuhani'
 * DESCRIPTION: This is an event class that will be used by a global
 *              event handler.
 * PREREQUISITE: libraries should be predefine in main.js
 * LAST MODIFIED FOR JIRA ISSUE: MAV-108
 **************************************************************************/
define([
    'jquery',     // lib/jquery/jquery
    'underscore', // lib/underscore/underscore
    'backbone'    // lib/backbone/backbone
], function ($, _, Backbone) {

     var Hub = function(){
        this.events = _.extend({}, Backbone.Events);
    }
    return Hub;
});

