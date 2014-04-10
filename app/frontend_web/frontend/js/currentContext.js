/***************************************************************************
 * Copyright (c) 2014 - Maven Medical
 * AUTHOR: 'Asmaa Aljuhani'
 * DESCRIPTION: This is an instance from the Model contextModel. This context
 *              will be used in all views. Passing an instance from a model
 *              make this object global, so all views can modify it.
 *              Based on this modification events will be triggered.
 * PREREQUISITE: libraries should be predefine in main.js
 * LAST MODIFIED FOR JIRA ISSUE: MAV-98
 **************************************************************************/
define([
    'jquery',     // lib/jquery/jquery
    'underscore', // lib/underscore/underscore
    'backbone',    // lib/backbone/backbone
    'models/contextModel'

], function ($, _, Backbone,Context) {
    var currentContext = new Context();

    return currentContext;

});








