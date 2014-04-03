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
    'views/widget/evidence'
], function ($, _, Backbone, currentContext, eventHub,  SideMenu, TopNav, HomeView, PatientView, EpisodeView, AlertsView, Evidence) {
    var AppRouter = Backbone.Router.extend({
        routes: {
            "": 'showHome',
            "patient": 'showPatient',
            "alerts": 'showAlerts',
            "episode": 'showEpisode',
            "episode/:id/patient/:id": 'episodeIDs',
            "episode/:id/patient/:id/evi/:id": 'showEvidence',

            //default
            '*action': 'defaultAction'
        },
        showHome: function () {
            currentContext.set({page:'home'});
            var homeView = new HomeView
        },
        showPatient: function () {
             console.log("show pat");
            //update current context page
            currentContext.set({page:'patient'});

            var patientView = new PatientView;
            patientView.render();
        },
        showAlerts: function () {
             console.log("show alert");
            var alertsView = new AlertsView;
            alertsView.render();
        },
        episodeIDs: function(enc, pat){
             console.log("epi id");
            currentContext.encounter = enc;
            currentContext.patient = pat;
            this.showEpisode()
        },
        showEpisode: function () {
            console.log(" Episode func");
            //update current context page
            currentContext.page = 'episode';
            var episodeView = new EpisodeView;

        },
        showEvidence: function (enc, pat, evi) {
            //update current context page
            currentContext.alert = evi;
            currentContext.encounter = enc;
            currentContext.patient = pat;

            var episodeView = new EpisodeView;

            var evidence = new Evidence;
            $('#evidence-' + currentContext.alert).modal();
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

    return AppRouter
});