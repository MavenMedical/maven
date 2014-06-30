define([
    // These are path alias that we configured in our main.js
    'jquery',     // lib/jquery/jquery
    'underscore', // lib/underscore/underscore
    'backbone',    // lib/backbone/backbone


], function ($, _, Backbone) {

    var Helpers = {

        detailHeadings: {'enc_pl_dx': "Encounter or Problem List Diagnosis", 'pl_dx': "Problem List Diagnosis",
            'hist_dx': "Historical Diagnosis", 'lab': "Lab Results", 'enc_dx': "Encounter Diagnosis", 'hist_proc': "Historic Procedure", 'enc_proc':"Encounter Procedure"},
        notDetail: ['id', 'evidence','genders', 'minAge', 'maxAge', 'name', 'triggers', 'triggerType', 'sources']
    };

    return Helpers;


});
