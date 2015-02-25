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
        jquery: ['//code.jquery.com/jquery-1.11.0.min', 'libs/jquery/jquery-min'],
        underscore: 'libs/underscore/underscore-min',
        backbone: ['libs/backbone/backbone', '//cdnjs.cloudflare.com/ajax/libs/backbone.js/1.1.2/backbone-min.js'],

    }


})
require([
    //Load our app module and pass it to our definition function
    'app',
    'jquery',
    'underscore',
    'text',

], function (App) {
    // The "app" dependency is passed in as "App"
    // Again, the other dependencies passed in are not "AMD" therefore don't pass a parameter to this function
    App.initialize();
});
