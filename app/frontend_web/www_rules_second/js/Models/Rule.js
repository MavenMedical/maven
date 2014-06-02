define([
    'jquery',
    'underscore',
    'backbone',
    'Collections/TriggerSet',
    'Collections/DetailsSet'
], function($, _, Backbone, TriggerSet, DetailsSet) {

    var Rule = Backbone.Model.extend({
        defaults: {'myTriggers':new TriggerSet({type: 'procedure'}), 'myDetails':new DetailsSet(), 'myName': "other"},
        initialize: function(params){

          if (params){
            this.set('myName', params.name);
          }
              this.set('myTriggers',new TriggerSet({type:'procedure'}));
              var set = this.get('myTriggers');
              set.remove(set.models[0]);
        },

        addDetail: function(detailParams){},
        addTrigger:function(triggerParams){},

        setName: function(nameIn){
            this.set('myName', nameIn);
        }


    });



    return Rule;

});
