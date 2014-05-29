define([
    'jquery',
    'underscore',
    'backbone',
    'ScreenModels/RuleBasePanel',
    'ScreenModels/NameEditor',
    'ScreenModels/TriggerSelectorPanel',

    'Helpers'

], function($, _, Backbone, RulerBasePanel, NameEditor, TriggerSelectorPanel, Helpers) {

    var RuleOverview = Backbone.Model.extend({

        defaults: {'curRule': null, 'RuleBasePanel': null, 'NameEditor': null, 'TriggerSelectorPanel': null},
        loadRule: function(params){


        },
        editName: function(){
            var nameEditor = new NameEditor(this.get('curRule'));
            this.set('NameEditor', nameEditor);
        },
        editSelectedTriggers: function(){

            var TriggerSelectorPanel = new TriggerSelectorPanel(this.get('curRule'));

            this.set('TriggerSelectorPanel', TriggerSelectorPanel);

        }
    });
    return RuleOverview;

});
