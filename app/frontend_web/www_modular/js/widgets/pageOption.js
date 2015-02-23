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
    //This view is used by widgets that has page options on the sidebar
    // each widget would use this view to append the option
    // options can be nested

    //each option is composed of icon and href and the label
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

    // a recursive function to handle nested options
    var appendOption = function (opt, list) {
        list = typeof list !== 'undefined' ? list : '#sidebar-list';
        for (o in opt) {
            var thisopt = opt[o]
            
            var option = elem(thisopt.page, thisopt.icon, o);
            if (thisopt.children) {
                $(option.children()[0]).append($('<b>', {'class': "arrow fa fa-angle-down"}))
                var suboption = $('<ul>', {'class': "submenu"});
                var submenu = thisopt.children;
                for (s in submenu) {
                    appendOption(submenu[s], suboption);
                }
                option.append(suboption);
            }
            option.appendTo(list);
            if (thisopt.init) {
                thisopt.init(option)
            }
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
            // pathway has special href so we need to add mor info for the url
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
