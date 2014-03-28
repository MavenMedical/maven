/**
 * Created by Asmaa Aljuhani on 3/11/14.
 */

define([
    'jquery',
    'underscore',
    'backbone',
    'bootstrap',
    'router', // Request router.js
], function ($, _, Backbone, Bootstrap, Router) {
    var initialize = function () {
        // Pass in our Router module and call it's initialize function
        Router.initialize();
    };

    return {
        initialize: initialize
    };
});