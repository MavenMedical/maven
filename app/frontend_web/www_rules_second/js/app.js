/**
 * Created by Asmaa Aljuhani on 3/11/14.
 */

define([
    'jquery',
    'underscore',
    'backbone',
    'bootstrap',
    'Views/BasicsPanelView',
    'Models/TriggerItem',
    'Views/RuleListView',
    'Models/RuleItem',
    'Views/TriggerEditorView',
    'Helpers'


], function ($, _, Backbone, Bootstrap, BasicsPanelView, TriggerItem, RuleListView, RuleItemModel, TriggerEditorView, Helpers) {
    var initialize = function () {

        var testPanel = new BasicsPanelView();
        var testItem1 = new RuleItemModel();
        var testRuleList = new RuleListView();
        var testTrigger = new TriggerItem();
        testRuleList.render();
        testPanel.model.addTrigger(testTrigger);
        testPanel.render();
        var testTEditor = new TriggerEditorView();
        testTEditor.render();

    };

    return {
        initialize: initialize
    };
});