/**
 * Created by Asmaa Aljuhani on 3/11/14.
 */

define([
    'jquery',
    'underscore',
    'backbone',
    'bootstrap',
    'router', // Request router.js
], function ($, _, Backbone, Bootstrap, AppRouter) {
    var initialize = function () {
        // Pass in our Router module and call it's initialize function
        new AppRouter;
    };

    return {
        initialize: initialize
    };
});