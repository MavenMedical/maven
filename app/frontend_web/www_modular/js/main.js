/***************************************************************************
 * Copyright (c) 2014 - Maven Medical
 * AUTHOR: 'Asmaa Aljuhani'
 * DESCRIPTION: This Javascript file holds all libraries that will be used
 *              by the MVC and Initialize the frontend App.
 * LAST MODIFIED FOR JIRA ISSUE: MAV-98
 **************************************************************************/

// Require.js allows us to configure shortcut alias
require.config({
    paths: {
        jquery: 'libs/jquery/jquery-min',
        jquery_ui: 'libs/fullCalendar/jquery-ui.custom.min',
        underscore: 'libs/underscore/underscore',
        backbone: 'libs/backbone/backbone',
        jsplumb: 'libs/jsplumb/jquery.jsPlumb-1.6.2-min',
        bootstrap: '../css/bootstrap/js/bootstrap.min',
        fullcalendar: 'libs/fullCalendar/fullcalendar.min',
        moment: 'libs/fullCalendar/moment.min',
	    templates: '../templates'
    },
    shim: {
        bootstrap :{
            deps: ['jquery']
        },
        jsplumb :{
          deps: ['jquery','jquery_ui']
        },
        fullCalendar :{
            deps: ['jquery','moment', 'jquery_ui']
        }
    }
});

require([
    //Load our app module and pass it to our definition function
    'app',
    'jquery',
    'underscore',
    'backbone',
    'bootstrap',
    'router',
    'globalmodels/contextModel',
    'globalmodels/patientModel',
    //    'globalmodels/spendingModel',
    //    'localmodels/patientRowModel',
    
    'text'
], function (App) {
    // The "app" dependency is passed in as "App"
    // Again, the other dependencies passed in are not "AMD" therefore don't pass a parameter to this function
    App.initialize();
});