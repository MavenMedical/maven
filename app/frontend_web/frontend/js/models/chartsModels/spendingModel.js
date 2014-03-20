/**
 * Created by Asmaa Aljuhani on 3/14/14.
 */

define([
    'underscore',
    'backbone'
], function (_, Backbone) {

    var SpendingModel = Backbone.Model.extend({
        urlRoot: '/spending'
    });

    return SpendingModel;
});