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

    //views
    'views/sidemenu',
    'views/topnav',

    'views/home',
    'views/patient',
    'views/episode',
    'views/alerts'
], function ($, _, Backbone,currentContext, SideMenu, TopNav, HomeView, PatientView, EpisodeView, AlertsView) {
    var AppRouter = Backbone.Router.extend({
        routes: {
            "": 'showHome',
            "patient/:id/details/:key": 'showPatient',
            "alerts": 'showAlerts',
            "episode/:id/details/:key": 'showEpisode',

            //default
            '*action': 'defaultAction'
        }
    });



    var initialize = function () {
        //ajaxPrefilter
        $.ajaxPrefilter(function (options, originalOptions, jqXHR) {
            options.url = 'services' + options.url;
        });

        var app_router = new AppRouter;

        // render side menu and topnav for all pages
        var sidemenu = new SideMenu;
        sidemenu.render();
        var topnav = new TopNav;
        topnav.render();

        app_router.on('route:showHome', function () {
            // Call render on the module we loaded in via the dependency array

            //update current context page
            currentContext.page = 'home';

            var homeView = new HomeView;

        });

        app_router.on('route:showPatient', function (patid , patkey) {

            //update current context page
            currentContext.page = 'patient';

            var patientView = new PatientView;
            patientView.render({id:patid, key:patkey});

        });
        app_router.on('route:showAlerts', function () {
            var alertsView = new AlertsView;
            alertsView.render();
        });
        app_router.on('route:showEpisode', function (patid, patkey) {


             //update current context page
            currentContext.page = 'episode';

            var episodeView = new EpisodeView;


        });
        app_router.on('defaultAction', function (actions) {
            console.log('No route:', actions);
        });

        Backbone.history.start();
    };

    return {
        initialize: initialize
    };
});