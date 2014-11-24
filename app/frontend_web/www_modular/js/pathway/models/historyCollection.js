define([
    'jquery',
    'underscore',
    'backbone',
    'globalmodels/contextModel',
    'globalmodels/scrollCollection',
], function($, _, Backbone, contextModel, ScrollCollection) {
    HistoryModel = Backbone.Model;

    var HistoryCollection = ScrollCollection.extend({
        url: function () {
            return '/history' + this.offset + '-' + (this.offset + this.limit);
        },
        model: HistoryModel,
        refresh: function () {
            if (contextModel.get('userAuth')) {
                //allow for additional data to be passed in, aside from the context model
                var data = {};
                $.extend(data, contextModel.toParams(), this.extraData);

                this.tried = 0;
                this.offset = 0;
                this.fetch({
                    data: $.param(data),
                    remove: true});
            }
        }
    });
    return HistoryCollection;
});
