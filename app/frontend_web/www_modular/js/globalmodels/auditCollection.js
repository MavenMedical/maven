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
        model: AuditModel,
        limit: 5,
        context: function(){
            $(".auditlist").on('show',
		    // make sure the correct audit list is being loaded (user's own list versus target user)
		    this.refresh);
        },
        refresh: function() {
            if (contextModel.get('userAuth')) {
                var data = {};
                $.extend(data, contextModel.toParams(), this.extraData);

                this.tried = 0;
                this.offset = 0;
                this.fetch({
                    data: $.param(data),
                    remove: true});
            }
        },
    });

    return AuditCollection;
});
