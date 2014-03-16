/**
 * Created by Asmaa Aljuhani on 3/14/14.
 */

define([
    'underscore',
    'backbone'
], function (_, Backbone) {

    var OrderModel = Backbone.Model.extend({
        urlRoot: '/order_details',
        defaults: {
            title : "Echocardiogram",
            order: "Followup ECG",
            cost: "$1200",
            reason: "Mitral regurgitation",
            evidence: "Don't test",
            ecost: "$0"
        }
    });

    return OrderModel;
});