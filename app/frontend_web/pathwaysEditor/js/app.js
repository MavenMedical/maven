
define([
    'jquery',
    'underscore',
    'backbone',
    'bootstrap',
    'models/contextModel',
    'models/nodeList',
    'widgets/TreeView'

], function ($, _, Backbone, Bootstrap,  contextModel, NodeList, TreeView) {//, TriggerList) {
    var initialize = function () {

        $.ajaxPrefilter(function (options, originalOptions, jqXHR) {
            options.url = 'rule_services' + options.url;
        });

        contextModel.setUser('tom', 'pw', '#');
         new TreeView({el:'#tree-view'});

    };



    return {
        initialize: initialize
    };
});
