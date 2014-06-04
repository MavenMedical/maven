define([
    'jquery',
    'underscore',
    'backbone',
    'models/contextModel'
], function($, _, Backbone, contextModel){
    var RuleModel = Backbone.Model.extend({url: '/rule'});

    var ruleModel = new RuleModel;
    if(contextModel.get('auth')) {

        ruleModel.fetch({data:$.param(contextModel.toParams())});


    }
    contextModel.on('change:id',
		    function(cm) {

			   console.log(ruleModel.fetch({data:$.param(contextModel.toParams())}));

		    }, ruleModel);
    return ruleModel;
});
