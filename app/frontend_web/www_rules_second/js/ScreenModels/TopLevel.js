define([
    'jquery',
    'underscore',
    'backbone',
    //Screen Models
    'ScreenModels/Overview',


    'Helpers'


], function($, _, Backbone, Overview, Helpers) {

    var TopLevel = Backbone.Model.extend({

        defaults: {centralFrame: new Overview()}


    });



    return TopLevel;

});
