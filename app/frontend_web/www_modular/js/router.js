
/***************************************************************************
 * Copyright (c) 2014 - Maven Medical
 * AUTHOR: 'Asmaa Aljuhani'
 * DESCRIPTION: This Javascript file has the main router functions that calls
 *               all other views.
 * PREREQUISITE: libraries should be predefine in main.js
 * LAST MODIFIED FOR JIRA ISSUE: MAV-98
 **************************************************************************/

define([
    'jquery',     // lib/jquery/jquery
    'underscore', // lib/underscore/underscore
    'backbone',    // lib/backbone/backbone,
    
    'globalmodels/contextModel',
], function ($, _, Backbone, currentContext) {
    
    var CheckLogin = function() {
	if (!currentContext.get('user') || !currentContext.get('userAuth')) {
	    currentContext.setUser('JHU1093124', 'notarealpassword', Backbone.history.fragment);  // hack for now
	    return false;
	}
	return true;
    };
    
    var showPage = function(user, userAuth) {
	if(user && user != currentContext.get('user')) {
	    console.log('pre-authenticated login');
	    currentContext.setUser(user,userAuth, Backbone.history.fragment);
	} else {
	    if (CheckLogin()) {
		console.log('showing page '+currentContext.get('page'));
		/* do more stuff here */
		window.scrollTo(0,0);
	    } else {
		console.log('trying to log in');
	    }
	}
    };
    
    var AppRouter = Backbone.Router.extend({
	routes: {
	    "(/login/:user/:userAuth)": 'showHome',
	    "patient/:id(/login/:user/:userAuth)": 'showPatient',
	    "episode/:id/patient/:id(/login/:user/:userAuth)": 'showEpisode',
	    "evidence/:id/patient/:id/evi/:id(/login/:user/:userAuth)": 'showEvidence',
	    //default
	    '*action': 'defaultAction'
	},
	showHome: function (user, userAuth) {
	    /* remove the current patient list, encounter, etc to revert the view to the doctor's user page */
	    currentContext.set({page:'home',patients:null,encounter:null,patientName:null});
	    showPage(user, userAuth);
	},
	showPatient: function (patid, user, userAuth) {
	    currentContext.set({page:'patient', encounter:null, patients:patid});
	    showPage(user, userAuth);
	},
	showEpisode: function(enc, pat, user, userAuth){
	    currentContext.set({page:'episode',encounter:enc,patients:pat});
	    showPage(user, userAuth);
	},
	showEvidence: function (enc, pat, evi, user, userAuth) {
	    currentContext.set({page:'episode',encounter:enc,patients:pat});
	    if(user && user != currentContext.get('user')) {
		currentContext.setUser(user,userAuth, Backbone.history.fragment);
	    } else {
		if(CheckLogin()) {
		    var evidence = new Evidence(evi);
		    $('#evidence-' + evi).modal();
		}
	    }
	},
	defaultAction: function (action) {
	    console.log('No route:', action);
	},
	
	
	initialize: function () {
	    //ajaxPrefilter
	    $.ajaxPrefilter(function (options, originalOptions, jqXHR) {
		options.url = 'services' + options.url;
	    });
	    Backbone.history.start();
	}
    });
    
    return AppRouter;
});
