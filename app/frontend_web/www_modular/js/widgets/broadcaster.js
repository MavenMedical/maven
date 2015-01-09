define(['jquery',
           'backbone',
           'underscore',
           'globalmodels/contextModel'

       ], function ($, backbone, _, contextModel) {
    var broadcaster = Backbone.view.extend({
                                               initialize: function () {
                                                   $.ajax({
                                                              data: $.param(contextModel.toParams()),
                                                              url: "/broadcaster",
                                                              success: beginPolling(),
                                                              fail: loginFailed
                                                          });


                                                   var loginFailed = function () {
                                                       var notification = new Notification("login failed")
                                                   }
                                                   var succeed = function () {

                                                       var notification = new Notification("maven notification")
                                                       beginPolling()
                                                   }

                                                   var fail = function () {
                                                       var notification = new Notification("failed connection")

                                                   }

                                                   var beginPolling = function () {
                                                       $.ajax({
                                                                  url: "/broadcaster/poll",
                                                                  success: succeed,
                                                                  failure: fail,
                                                                  dataType: "json"
                                                              });
                                                   };
                                               }
                                           })
    return broadcaster


})


