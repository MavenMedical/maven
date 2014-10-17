define([
    'jquery',
    'underscore',
    'backbone',
    'globalmodels/contextModel',
    'globalmodels/scrollCollection'
], function($, _, Backbone, contextModel, ScrollCollection) {
    AuditModel = Backbone.Model;

    var AuditCollection = ScrollCollection.extend({
        url: function() {return '/audits'+this.offset+'-'+(this.offset+this.limit);},
        extraData: {},
        model: AuditModel,
        limit: 5,
        context: function(){
            $(".auditlist").on('show',
		        // this will be needed once the context filters things
                function(cm) {
                if(true && cm.get('userAuth')) {
                    var data = {};
                    $.extend(data, contextModel.toParams(), this.extraData);

                    this.tried = 0;
                    this.offset = 0;
                    auditCollection.fetch({
                        data:$.param(data),
                        remove:true});
                }
            }, AuditCollection);
        },
    });

    return AuditCollection;
});
