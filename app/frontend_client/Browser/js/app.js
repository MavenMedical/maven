/**
 * Created by Asmaa Aljuhani on 3/11/14.
 */

define([
    'jquery',
    'underscore',
    'backbone',
], function ($, _, Backbone) {
    var initialize = function () {


    $.ajax({url: "",
                success: beginPolling(),
                fail: loginFailed
               });


    var loginFailed = function(){
        var notification = new Notification("login failed")
    }
    var succeed = function(){

        var notification = new Notification("maven notification")
        beginPolling()
    }

    var fail = function(){
        var notification = new Notification("failed connection")

    }

    var beginPolling = function(){
         $.ajax({
            url: "/broadcaster/poll",
            success: succeed,
            failure: fail,
            dataType: "json"});
        };

    }
    return {
        initialize: initialize
    };
});
