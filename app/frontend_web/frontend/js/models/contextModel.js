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
	urlRoot: '/services/login',
        defaults: {
            page: null,
            user: 'JHU1093124',
	    userAuth: '',
	    display: 'Dr. XYZ',
            patients: '',
            patientAuth: '',
            provider: null,
            encounter: null,
            department: null,
            alert: null
        },
        initialize: function () {
		this.fetch({
			success: function (res) {
			    console.log(res);
			},
			data: JSON.stringify({user:'JHU1093124', password:'notapassword'}),
			type: 'POST'
		    });
		
	    }

    });
    return Context;
});












