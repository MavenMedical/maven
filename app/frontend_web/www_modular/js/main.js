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
        //jquery: ['//code.jquery.com/jquery-1.11.0.min', 'libs/jquery/jquery-min'],
        jquery: ['libs/jquery/jquery-min'],
        jquery_ui: ['//code.jquery.com/ui/1.10.1/jquery-ui.min', 'libs/jquery/jquery-ui.min'],
        jquery_autocomplete: 'libs/jquery/jquery.ui.autocomplete.html',
	    touch: 'libs/jquery/jquery.ui.touch-punch.min',
        underscore: 'libs/underscore/underscore-min',
        backbone: ['libs/backbone/backbone', '//cdnjs.cloudflare.com/ajax/libs/backbone.js/1.1.2/backbone-min.js'],
        jsplumb: ['libs/jsplumb2/js/jquery.jsPlumb-1.6.2-min', 'libs/jsplumb2/js/jsplumb'],
        //bootstrap: ['//maxcdn.bootstrapcdn.com/bootstrap/3.1.1/js/bootstrap.min', '../css/bootstrap/js/bootstrap.min'],
        bootstrap: '../css/bootstrap/js/bootstrap.min',
	    bootstrapswitch: 'libs/bootstrap-switch/bootstrap-switch',
	    nestedSortable: 'libs/nestedSortable/nestedSortable',
        fullcalendar: 'libs/fullCalendar/fullcalendar.min',
        moment: 'libs/fullCalendar/moment.min',
        ckeditor2: 'libs/ckeditor/ckeditor',
        ckeditor: 'ckeditor-customize',
        templates: '../templates',
        amchartspie: 'libs/amcharts/pie',
        amchartslight: 'libs/amcharts/themes/light',
        amchartsserial: 'libs/amcharts/serial',
        amcharts: 'libs/amcharts/amcharts',
        ace: 'ace-min'
    },
    shim: {
	    touch: {deps: ['jquery_ui']},
        ace: {deps: ['jquery', 'jquery_ui','bootstrap']},
        'ace/assets/js/flot/jquery.flot.pie': {deps: ['ace/assets/js/flot/jquery.flot']},
        'ace/assets/js/flot/jquery.flot.resize': {deps: ['ace/assets/js/flot/jquery.flot']},
        bootstrap: {
            deps: ['jquery', 'jquery_ui']
        },
        bootstrapswitch: {
            deps: ['jquery', 'jquery_ui', 'bootstrap']
        },
        jsplumb: {
            deps: ['jquery', 'jquery_ui']
        },
        fullCalendar: {
            deps: ['jquery', 'moment', 'jquery_ui']
        },
        jquery_ui: {
            deps: ['jquery']
        },
        amchartspie: { deps: ['amcharts'], exports: 'AmCharts', init: function () {
            AmCharts.isReady = true;
        }},
        amchartsserial: { deps: ['amcharts'], exports: 'AmCharts', init: function () {
            AmCharts.isReady = true;
        }},
        amchartslight: { deps: ['amcharts'], exports: 'AmCharts', init: function () {
            AmCharts.isReady = true;
        }},
    }
});

require([
    //Load our app module and pass it to our definition function
    'app',
    'jquery',
    'touch',
    'underscore',
    'backbone',
    'bootstrap',
    'bootstrapswitch',
    'ace',
    'text',

], function (App) {
    // The "app" dependency is passed in as "App"
    // Again, the other dependencies passed in are not "AMD" therefore don't pass a parameter to this function

    App.initialize();
});
