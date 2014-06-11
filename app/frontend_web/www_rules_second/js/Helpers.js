define([
    // These are path alias that we configured in our main.js
    'jquery',     // lib/jquery/jquery
    'underscore', // lib/underscore/underscore
    'backbone',    // lib/backbone/backbone


], function ($, _, Backbone) {

    var Helpers = {

        detailHeadings: {'pl_dx': "Problem List Diagnosis", 'hist_dx': "Historical Diagnosis", 'lab': "Lab Results"}

    };

    return Helpers;


});
