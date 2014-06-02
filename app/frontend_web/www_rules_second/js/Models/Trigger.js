define([
    'jquery',
    'underscore',
    'backbone',
    'Helpers',

], function($, _, Backbone, Helpers) {

    var Trigger = Backbone.Model.extend({
        defaults: {'code': null, 'triggerType': null, 'id':-1},
        initialize: function(params){
          this.set('triggerType', params.triggerType);
          this.set('code', params.code);
          if (params.id){
              this.set('id', params.id);
          } else {
              this.set('id', Helpers.getNewTriggerID());

          }
        },
        getDescription: function(){
            var ret =  "Rule will trigger when ";
            if (this.get('type')=='procedure'){
                  ret += " procedure with CPT code "
            } else {
                ret += " drug with Snomed code "
            }
            ret += this.get('code');
            ret += " is ordered";
            return ret;
        }


    });



    return Trigger;

});
