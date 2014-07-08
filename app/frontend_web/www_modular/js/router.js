
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
    'widgets/evidence',
    'widgets/login',
], function ($, _, Backbone, currentContext, Evidence, Login) {
    
    var CheckLogin = function() {
	if (!currentContext.get('user') || !currentContext.get('userAuth')) {
	    new Login({el: '#login-modal'})
	    return false;
	}
	return true;
    };
    
    var showPage = function(provider, customer, userAuth) {
	if(provider && !currentContext.get('user')) {
	    console.log('pre-authenticated login');
	    currentContext.setProvider(provider, customer, userAuth);
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
	    "(/login/:provider/:customer/:userAuth)": 'showHome',
	    "patient/:id(/login/:provider/:customer/:userAuth)": 'showPatient',
	    "episode/:id/patient/:id/:date(/login/:provider/:customer/:userAuth)": 'showEpisode',
	    "evidence/:id/patient/:id/evi/:id(/login/:provider/:customer/:userAuth)": 'showEvidence',
	    "logout": 'logout',
	    //default
	    '*action': 'defaultAction'
	},
	showHome: function (provider, customer, userAuth) {
	    /* remove the current patient list, encounter, etc to revert the view to the doctor's user page */
	    currentContext.set({page:'home',patients:null,encounter:null,patientName:null});
	    showPage(provider, customer, userAuth);
	},
	showPatient: function (patid, provider, customer, userAuth) {
	    currentContext.set({page:'patient', encounter:null, patients:patid});
	    showPage(provider, customer, userAuth);
	},
	showEpisode: function(enc, pat, date, provider, customer, userAuth){
	    currentContext.set({page:'episode',encounter:enc,patients:pat, enc_date:date});
	    showPage(provider, customer, userAuth);
	},
	showEvidence: function (enc, pat, evi, provider, customer, userAuth) {
	    currentContext.set({page:'episode',encounter:enc,patients:pat});
	    if(provider && provider != currentContext.get('user')) {
		currentContext.setProvider(provider, customer, userAuth);
	    } else {
		if(CheckLogin()) {
		    var evidence = new Evidence({'evi':evi});
		    //$('#evidence-' + evi).modal();
		}
	    }
	},
	logout: function() {
	    currentContext.clear({silent:true});
	    location.href="/index.html";
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
