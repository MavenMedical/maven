
define([
    'jquery',
    'underscore',
    'backbone',
    'bootstrap',
    'router', //Request router.js

], function ($, _, Backbone, Bootstrap, AppRouter) {//, TriggerList) {
    var initialize = function () {

        /*$.ajaxPrefilter(function (options, originalOptions, jqXHR) {
            options.url = 'rule_services' + options.url;
        });*/


         new AppRouter;

    };



    return {
        initialize: initialize
    };
});
