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

    'currentContext',
    'eventhub',

    //views
    'views/sidemenu',
    'views/topnav',

    'views/home',
    'views/patient',
    'views/episode',
    'views/alerts',
    'views/widget/evidence',

     'text!templates/templatesA/skeleton.html'
], function ($, _, Backbone, currentContext, eventHub,  SideMenu, TopNav, HomeView, PatientView, EpisodeView, AlertsView, Evidence, skeletonA) {

    var CheckLogin = function() {
	if (!currentContext.get('user') || !currentContext.get('userAuth')) {
	    currentContext.setUser(CheckSkeleton, 'JHU1093124', 'notarealpassword', Backbone.history.fragment);  // hack for now
	    return false;
	}
	return true;
    };

    // This function is to determine which layout to display
    var CheckSkeleton = function(){
        if (currentContext.get('layout') == 'a'){
            $('body').html(_.template(skeletonA));
        }
        else if (currentContext.get('layout') == 'b')
        {
            //alert('b');
        }
    }


    var AppRouter = Backbone.Router.extend({
        routes: {
            "": 'showHome',
            "patient": 'showPatient',
            "alerts": 'showAlerts',
            "episode": 'showEpisode',
            "episode/:id/patient/:id(/login/:user/:userAuth)": 'episodeIDs',
            "episode/:id/patient/:id/evi/:id(/login/:user/:userAuth)": 'showEvidence',

            //default
            '*action': 'defaultAction'
        },
        showHome: function () {
		//alert('showing home');
		if (CheckLogin()) {
		    currentContext.set({page:'home',patients:null,encounter:null,patientName:null});
		    var homeView = new HomeView
		}
        },
        showPatient: function () {
		if (CheckLogin()) {
		    console.log("show pat");
		    //update current context page
		    currentContext.set({page:'patient'});
		    
		    var patientView = new PatientView;
		    patientView.render();
		}
        },
        showAlerts: function () {
		if (CheckLogin()) {
		    console.log("show alert");
		    var alertsView = new AlertsView;
		    alertsView.render();
		};
        },
        episodeIDs: function(enc, pat, user, userAuth){
             console.log("epi id");
	     currentContext.set({encounter:enc,patients:pat});
	     if(user && user != currentContext.get('user')) {
		 currentContext.setUser(user,userAuth, Backbone.history.fragment);
	     } else {
		 this.showEpisode()
	     }
        },
        showEpisode: function () {
		if(CheckLogin()) {
		    console.log(" Episode func");
		    //update current context page
		    currentContext.set({page:'episode'});
		    var episodeView = new EpisodeView;
		};

        },
        showEvidence: function (enc, pat, evi, user, userAuth) {
            //update current context page
		currentContext.set({encounter:enc,patients:pat});
		if(user && user != currentContext.get('user')) {
		currentContext.setUser(user,userAuth, Backbone.history.fragment);
	    } else {
		if(CheckLogin()) {
		    var episodeView = new EpisodeView;
		    
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
            // render side menu and topnav for all pages
            var sidemenu = new SideMenu;
            sidemenu.render();
            var topnav = new TopNav;
            topnav.render();
	    Backbone.history.start();
        }
    });

    return AppRouter;
});