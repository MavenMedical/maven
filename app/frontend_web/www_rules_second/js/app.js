
define([
    'jquery',
    'underscore',
    'backbone',
    'bootstrap',

    'models/contextModel',
    'models/ruleModel',

    //Views
    'widgets/ruleList',
    'widgets/ruleOverview',
    'widgets/triggerEditor',
    'widgets/detailOverview',
    'widgets/evidenceEditor',
    'widgets/SourceManager'
//    'widgets/triggerList',
], function ($, _, Backbone, Bootstrap, contextModel, curRule,  RuleList, RuleOverview, TriggerEditor, DetailOverview, EvidenceEditor, SourceManager) {//, TriggerList) {
    var initialize = function () {
        $.ajaxPrefilter(function (options, originalOptions, jqXHR) {
            options.url = 'rule_services' + options.url;
        });

        contextModel.setUser('tom', 'pw', '#');
         (new RuleList({el:$("#rule-list")})).render();
         new RuleOverview({el:$("#rule-overview")});
         new DetailOverview({el:$("#detail-list")});
        curRule.on('sync', function(){
            new SourceManager({el: $('#source-manager', this.$el)})
        }, this)

         contextModel.on('change:auth', function(){
            new EvidenceEditor({el:$("#evi-list")});
            new TriggerEditor({el:$("#trigger-editor")});
         }, this);

    };


    return {
        initialize: initialize
    };
});
