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
        jquery_ui: 'libs/jquery/jquery-ui.min',
        jquery_autocomplete: 'libs/jquery/jquery.ui.autocomplete.html',
        underscore: 'libs/underscore/underscore',
        backbone: 'libs/backbone/backbone',
        jsplumb: 'libs/jsplumb2/js/jsplumb',
        bootstrap: '../css/bootstrap/js/bootstrap.min',
        fullcalendar: 'libs/fullCalendar/fullcalendar.min',
        moment: 'libs/fullCalendar/moment.min',
	templates: '../templates',
	amchartspie: 'libs/amcharts/pie',
	amchartslight: 'libs/amcharts/themes/light',
	amchartsserial: 'libs/amcharts/serial',
	amcharts: 'libs/amcharts/amcharts',
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
        },
	jquery_ui: {
	    deps: ['jquery'],
	},
	amchartspie: { deps: ['amcharts'], exports: 'AmCharts', init: function() {AmCharts.isReady = true;}},
	amchartsserial: { deps: ['amcharts'], exports: 'AmCharts', init: function() {AmCharts.isReady = true;}},
	amchartslight: { deps: ['amcharts'], exports: 'AmCharts', init: function() {AmCharts.isReady = true;}},
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
    'text',
    'jsplumb'
], function (App) {
    // The "app" dependency is passed in as "App"
    // Again, the other dependencies passed in are not "AMD" therefore don't pass a parameter to this function
    App.initialize();
});
