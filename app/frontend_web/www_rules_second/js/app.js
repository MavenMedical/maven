
define([
    'jquery',
    'underscore',
    'backbone',
    'bootstrap',

    'models/contextModel',
    //Views
    'widgets/ruleList',
    'widgets/ruleInfo',
//    'widgets/triggerList',
], function ($, _, Backbone, Bootstrap, contextModel, RuleList, RuleInfo) {//, TriggerList) {
    var initialize = function () {
        $.ajaxPrefilter(function (options, originalOptions, jqXHR) {
            options.url = 'rule_services' + options.url;
        });
 
	contextModel.setUser('tom', 'pw', '#');

	(new RuleList({el:$("#fixed-left")})).render();
	new RuleInfo({el:$("#floating-top")});
//	(new TriggerList({el:$("#main-content")})).render();

    };

    return {
        initialize: initialize
    };
});
