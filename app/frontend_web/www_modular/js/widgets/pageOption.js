/**
 * Created by devel on 11/20/14.
 */
define([
    // These are path alias that we configured in our main.js
    'jquery',     // lib/jquery/jquery
    'underscore', // lib/underscore/underscore
    'backbone',   // lib/backbone/backbone
    'globalmodels/contextModel'
], function ($, _, Backbone, contextModel) {
    var elem = function (page, icon, menu_text) {
        return $('<li>', {}).append(
            $('<a>', {
                'href': page,
                'class': "dropdown-toggle"}).append(
                $('<i>', {
                    'class': 'menu-icon fa ' + icon}))
                .append(
                $('<span>', {
                    'class': 'menu-text',
                    'text': menu_text})
            )
                .append(
                $('<b>', {'class': "arrow"})
            )
        )
    };

    var appendOption = function (opt, list) {
        list = typeof list !== 'undefined' ? list : '#sidebar-list';
        for (o in opt) {
            var option = elem(opt[o][1], opt[o][0], o);
            if (opt[o].length == 3) {
                $(option.children()[0]).append($('<b>', {'class': "arrow fa fa-angle-down"}))
                var suboption = $('<ul>', {'class': "submenu"});
                var submenu = opt[o][2];
                for (s in submenu) {
                    appendOption(submenu[s], suboption);
                }
                option.append(suboption);
            }
            option.appendTo(list);
        }

    };

    var pageOption = Backbone.View.extend({
        el: '#sidebar-list',
        initialize: function (opt, list) {
            list = typeof list !== 'undefined' ? list : '#sidebar-list';
            appendOption(opt, list);
            this.$el.off('click');
        },
        events:{
            'click a':'setPage'
        },
       setPage: function(e){
            e.preventDefault();

           var href = $(e.currentTarget).attr("href");
           
            if(href =='pathway'){
                Backbone.history.navigate("pathway/" + contextModel.get('pathid') + "/node/" + contextModel.get('code'), {trigger: true});
            }
            else if (href == 'pathwayEditor'){
                Backbone.history.navigate("pathwayeditor/" + contextModel.get('pathid') +"/node/" + contextModel.get('code') , true);
            }
            else
            {
              Backbone.history.navigate(href, true);
            }

           console.log('page option', contextModel.get('page'));

        }
    });
    return pageOption;
});
