define([
    'jquery',
    'underscore',
    'backbone',
    'Collections/RuleSet',

    'Helpers'

], function($, _, Backbone, RuleSet, Helpers) {

    var RuleListDisplay = Backbone.Model.extend({

        defaults: {'myRuleSet': new RuleSet(), 'myOverview': null},
        initialize: function(){
            this.set('myRuleSet', new RuleSet);


        },
        addRule: function(ruleIn){
            ruleIn.on('change:myName', function(){
                this.trigger('happened');
            },this)
            this.get('myRuleSet').add(ruleIn);
        },
        deleteRule: function(toDelete){

          this.get('myRuleSet').remove(toDelete);

        }
    });
    return RuleListDisplay;

});
