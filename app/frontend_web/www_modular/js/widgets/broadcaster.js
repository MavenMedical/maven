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


                if (self.curNotification.models.length > 0 ){
                    var notification = new Notification("Maven Alert", {
                        body: "There is a standard of care for this patient.\n Click to view the pathway." ,
                        icon: "http://localhost/images/temp/newPath.jpg"
                    })
                    notification.addEventListener("click", function () {
                        window.open(self.curNotification[0])
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


