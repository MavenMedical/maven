/**
 * Created by Asmaa Aljuhani on 3/11/14.
 * DESCREPTION: This Javascript file initialize the router.
 */

define([
    'jquery',
    'underscore',
    'backbone',
    'bootstrap',
    'router',
    'widgets/sidebar'
], function ($, _, Backbone, Bootstrap, AppRouter, Sidebar) {
    var initialize = function () {

        // Pass in our Router module and        call it's initialize function
        new AppRouter;
        new Sidebar;
    };

    return {
        initialize: initialize
    };
});
