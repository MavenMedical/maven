/**
 * Created by Asmaa Aljuhani on 3/14/14.
 */

define([
    'underscore',
    'backbone'
], function (_, Backbone) {

    var EncounterModel = Backbone.Model.extend({
        defaults: {
            Date: "12/13/12",
            utilization: "$95,100",
            saving: "$60,700"
        },
        initialize: function () {
            //nested collection
            // this.forward("orders", new OrderCollection);
        }
    });

    return EncounterModel;
});