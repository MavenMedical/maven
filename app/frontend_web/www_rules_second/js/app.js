
define([
    'jquery',
    'underscore',
    'backbone',
    'bootstrap',

    'models/contextModel',
    //Views
    'widgets/ruleList',
], function ($, _, Backbone, Bootstrap, contextModel, RuleList) {
    var initialize = function () {
        $.ajaxPrefilter(function (options, originalOptions, jqXHR) {
            options.url = 'rule_services' + options.url;
        });
 
	contextModel.setUser('tom', 'pw', '#');

	(new RuleList({el:$("#fixed-left")})).render();

    };

    return {
        initialize: initialize
    };
});
