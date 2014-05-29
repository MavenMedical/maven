define([
    'jquery',
    'underscore',
    'backbone',
    'Collections/TriggerSet',
    'Collections/DetailsSet'
], function($, _, Backbone, TriggerSet, DetailsSet) {

    var Rule = Backbone.Model.extend({
        defaults: {'myTriggers':new TriggerSet({type: 'procedure'}), 'myDetails':new DetailsSet(), 'myName': "defaultName"},
        initialize: function(params){
          if (params.name)
              this.set('myName', params.name);
        },

        addDetail: function(detailParams){},
        addTrigger:function(triggerParams){},

        setName: function(nameIn){
            this.set('myName', nameIn);
        }


    });



    return Rule;

});
