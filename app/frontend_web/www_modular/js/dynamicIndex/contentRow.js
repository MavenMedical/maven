
define([
    'jquery',
    'backbone',
    'underscore',
    'globalmodels/contextModel',
    'text!templates/contentRow.html'
    ],
    function($, _, backbone, contextModel){

        var contentRow = Backbone.View.extend({
            el: $('#dynamic-content'),
            initialize: function(widget, template, el){
                console.log(el)
                if (el)
                    this.activeWidget = new widget({template: template, el: el})
                else
                    this.activeWidget = new widget({template: template})
                if (!el)
                    this.$el.append(this.activeWidget.$el)
                this.control = $('.widget-column', this.activeWidget.$el)
            },
            hide: function(){
                this.control.hide();
            },
            show: function(){
                this.control.show()
            }




        })
        return contentRow



    });
