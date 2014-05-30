define([
    'jquery',
    'underscore',
    'backbone',



    'Helpers'


], function($, _, Backbone, Helpers) {

    var TopLevel = Backbone.Model.extend({
        defaults: {'name': null},
        initialize: function(ruleIn){
            this.setName(ruleIn.getName);
        },

        getName: function(){
            return this.get('name');
        },

        setName: function(param){
            this.set('name', param);
        }


    });



    return TopLevel;

});
