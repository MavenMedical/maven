define(['jquery',
    'backbone',
    'underscore',
    'globalmodels/contextModel'

], function ($, Backbone, _, contextModel) {
    var notificationSet = Backbone.Collection.extend({
        url: "/broadcaster/poll"
    })


    var broadcaster = Backbone.View.extend({
        initialize: function () {
            var self = this;
            this.curNotification = new notificationSet();
            this.curNotification.on('sync', function (model, changes) {
                var outputString = ""
                for (var i in changes) {
                    var value = changes[i]
                    console.log(value)
                    outputString += value
                    outputString += "\n"


                }
                if (outputString != ""){
                    var notification = new Notification("Maven Alert", {body: outputString, icon: "http://localhost/images/temp/newPath.jpg"})
                    notification.addEventListener("click", function () {
                        alert("notification clicked")
                    })
                }
                self.beginPolling()

            })
            this.beginPolling()


        },
        loginFailed: function () {
        },


        beginPolling: function () {
            Notification.requestPermission()
            var self = this;
            this.curNotification.fetch({

                error: function () {
                    console.log('polling error')

                    setTimeout(self.beginPolling, 10000)
                }
            });

        }
    })


    return broadcaster


})


