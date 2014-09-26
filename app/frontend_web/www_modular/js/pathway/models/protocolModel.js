/**
 * Created by Asmaa Aljuhani on 9/26/14.
 */
define([
    'jquery',
    'underscore',
    'backbone',
   'globalmodels/contextModel',

], function($, _, Backbone, contextModel){
    var protocolNode = Backbone.Model.extend({
        initialize: function(params){
          this.set('protocol', params.protocol)
          this.set('noteToCopy', params.noteToCopy)
        },
        getNodeType: function(){
          return "protocolNode"
        }
    });

    return protocolNode;

})