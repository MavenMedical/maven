/**
 * Created by Tom DuBois on 3/28/14.
 */

define([
    'underscore',
    'backbone'
], function (_, Backbone) {

    var UtilizationModel = Backbone.Model.extend({
        urlRoot: '/total_spend',
        defaults: {
		spending:10,
		savings:1
        }
    });

    return UtilizationModel;

});