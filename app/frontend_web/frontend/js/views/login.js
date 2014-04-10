/**
 * Created by devel on 4/3/14.
 */

define([
    // These are path alias that we configured in our main.js
    'jquery',     // lib/jquery/jquery
    'underscore', // lib/underscore/underscore
    'backbone',    // lib/backbone/backbone
], function ($, _, Backbone) {

    var LogIn = Backbone.View.extend({
        render: function(){
            $('body')
        }
    });

    return LogIn;
    // What we return here will be used by other modules
});
