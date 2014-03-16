/**
 * Created by Asmaa Aljuhani on 3/14/14.
 */

define([
    'underscore',
    'backbone'
], function (_, Backbone) {

    var AlertModel = Backbone.Model.extend({
        urlRoot: '/alert_details',
        defaults: {
            title : "Avoid NSAIDS",
            date: "12/15/2013",
            action: "Ignored",
            cost: "$168",
            details: "Avoid nonsteroidal anti-inflammatory drugs (NSAIDS) in indeviduals with hypertension or heart failure or CKD of all causes, including diabetes.",
            link: "An-Online.org"
        }
    });

    return AlertModel;
});