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
        underscore: 'libs/underscore/underscore',
        backbone: 'libs/backbone/backbone',
        bootstrap: '../css/bootstrap/js/bootstrap.min',
        jsplumb: 'libs/jsplumb',

	templates: '../templates'
    },
    shim: {
        bootstrap :{
            deps: ['jquery']
        }
    }
});

require([
    //Load our app module and pass it to our definition function
    'app',
    'jquery',
    'underscore',
    'backbone',
    'jsplumb/js/jsplumb',
    //    'globalmodels/spendingModel',
    //    'localmodels/patientRowModel',
    
    'text'






], function (App) {

    // The "app" dependency is passed in as "App"
    // Again, the other dependencies passed in are not "AMD" therefore don't pass a parameter to this function
    App.initialize();
});