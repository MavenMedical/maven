/**
 * Created by Asmaa Aljuhani on 3/14/14.
 */

define([
    // These are path alias that we configured in our main.js
    'jquery',     // lib/jquery/jquery
    'underscore', // lib/underscore/underscore
    'backbone',    // lib/backbone/backbone

], function () {
    var currentContext = {
        user: 'tom',
        patient: null,
        provider: null,
        encounter: null,
        department: null
    };
    return currentContext;
    // What we return here will be used by other modules
});




