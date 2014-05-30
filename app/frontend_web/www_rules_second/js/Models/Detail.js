define([
    'jquery',
    'underscore',
    'backbone',
    'Helpers'

], function($, _, Backbone, Helpers) {

    var Rule = Backbone.Model.extend({
        id: 0,
        defaults: {'detJSON': {}},
        initialize: function(params){
          if (params.id){
              this.id = params.id;
          } else {
              this.id = Helpers.getNewDetailID();
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



    return Rule;

});
