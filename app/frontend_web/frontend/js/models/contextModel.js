/***************************************************************************
 * Copyright (c) 2014 - Maven Medical
 * AUTHOR: 'Asmaa Aljuhani'
 * DESCRIPTION: This Javascript file is for context that will be used within
 *              the application.
 *              This file needed to be called in all other modules.
 * PREREQUISITE: libraries should be predefine in main.js
 * LAST MODIFIED FOR JIRA ISSUE: MAV-98
 **************************************************************************/

define([
    'jquery',     // lib/jquery/jquery
    'underscore', // lib/underscore/underscore
    'backbone'    // lib/backbone/backbone
], function ($, _, Backbone) {

    var Context = Backbone.Model.extend({
        defaults: {
            page: null,
            user: 'tom',
            patients: '1&2&3&4',
            key: '1U6BAcMeDWIN5_MyUd971tUU8jUk3F_R',
            provider: null,
            encounter: null,
            department: null,
            alert: null
        },
        initialize: function () {
        }

    });
    return Context;
});












