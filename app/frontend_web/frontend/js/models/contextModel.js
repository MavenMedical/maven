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
    'backbone',    // lib/backbone/backbone
	], function ($, _, Backbone) {
	   
	   function setActiveStyleSheet(title) {
	       var i, a, main;
	       for(i=0; (a = document.getElementsByTagName("link")[i]); i++) {
		   if(a.getAttribute("rel").indexOf("style") != -1 && a.getAttribute("title")) {
		       a.disabled = true;
		       if(a.getAttribute("title") == title) a.disabled = false;
		   }
	       }
	   }

    var Context = Backbone.Model.extend({
	urlRoot: '/login',
        defaults: {
            page: null,
            user: 'JHU1093124',
	    userAuth: '',
	    display: 'Dr. XYZ',
            patients: '',
            patientAuth: '',
	    patientName:'',
            provider: null,
            encounter: null,
            department: null
         },
        setUser: function (cb, user, pw, route) {
		if (this.user != user || !this.userAuth) {
		    this.set('user', user);
		    //alert('setting user');
		    this.fetch({
			    success: function (res) {
				cb();
				setActiveStyleSheet(res.get('stylesheet'));
				Backbone.history.loadUrl(route);
			    },
				data: JSON.stringify({user:user, password:pw}),
				type: 'POST'
				});
		}
	    }
	
	});

    return Context;
});
//'JHU1093124











