define([
    'jquery',
    'underscore',
    'backbone',
    'globalmodels/contextModel',
    'globalmodels/scrollCollection'
], function($, _, Backbone, contextModel, ScrollCollection) {
    AuditModel = Backbone.Model;

    auditCollection = new ScrollCollection;
    auditCollection.url = function() {return '/audits'+this.offset+'-'+(this.offset+this.limit);};
    //auditCollection.data = "target_user=1";
    auditCollection.model = AuditModel;
    auditCollection.limit = 5;
    auditCollection.context = function(){
        contextModel.on('change:patients change:encounter change:startdate change:enddate',
		    // this will be needed once the context filters things
		    function(cm) {
			if(true && cm.get('userAuth')) {
                this.tried = 0;
                this.offset = 0;
                auditCollection.fetch({
                    data:$.param(contextModel.toParams()),
                    remove:true});
			}
        }, auditCollection);
    };

    //auditCollection.initialize();

    return auditCollection;
});
