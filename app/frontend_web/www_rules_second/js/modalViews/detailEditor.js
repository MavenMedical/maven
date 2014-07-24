
define([
    // These are path alias that we configured in our main.js
    'jquery',     // lib/jquery/jquery
    'underscore', // lib/underscore/underscore
    'backbone',    // lib/backbone/backbone
    'Helpers',
    'internalViews/detailSearchBox',
    'internalViews/multiSelectSearch',
    'internalViews/routeListBox',
    'models/ruleModel'


], function ($, _, Backbone, Helpers, detailSearchBox, multiSelectSearch, routeListBox, curRule) {

    var DetailEditor = Backbone.View.extend({


        initialize: function(param){
            this.model = param.model;
            this.newDetail = param.newDetail
            this.$el = param.el;
            this.template = param.template
            this.type = param.type;
            this.$el.html(this.template());
            var searchEl = $('.search', this.$el)
            this.searchBoxes =[];
            if (searchEl.length!=0){
                var anon =  Backbone.Collection.extend( {url: '/search'})
                var searchBox = new detailSearchBox({collection: new anon(), type: this.type, el: searchEl})
                searchBox.render();
                this.searchBoxes.push(searchBox)
            }
            var multiSearchEl = $('.multi-select-search', this.$el)
            $.each(multiSearchEl, function(a, cur){
                var anon =  Backbone.Collection.extend( {url: '/search'})
                var searchBox = new multiSelectSearch({avail: new anon(), type: cur.getAttribute("type"), el: multiSearchEl, selected: new Backbone.Collection})
            })
            var routeListEl = $('.route-list', this.$el)
            $.each(routeListEl, function(a, cur){
                var listBox = new routeListBox({el: cur})
            })
            if (!this.newDetail){
                this.fillTemplate();
            }
            this.$el.show();


            var panel = this;
            $('.confirm-detail-button', this.$el)[0].onclick = function(){
                if (panel.searchBoxes.length>0){
                    for (var cur in panel.searchBoxes){
                        if (!panel.searchBoxes[cur].ready){
                            alert("Constraint is not complete, make sure you have a value selected in all search boxes")
                            return;
                        }
                    }
                }
                var inputs = $('.detail-input', panel.$el);
                for (var i=0;i<inputs.length;i++){
                    var cur = inputs[i];
                    if ($(cur).hasClass('hasTerm')){

                        _.each(cur, function(current){
                            if (current.selected){
                                _.each(current.attributes, function(curAttrib){
                                    panel.model.set(curAttrib.name, curAttrib.value);
                                })
                            }
                        })
                    }
                    panel.model.set(cur.getAttribute('name'), cur.value);


                }
                var multi = $('.multi-select-search', this.$el)
                _.each(multi, function(cur){
                    var selectedItems = $('.selected-items option', cur)
                    var idList = [];
                    _.each(selectedItems, function(cur){
                        idList.push(cur.value)
                    })
                    panel.model.set(cur.getAttribute('name'), idList);
                }, this)
                if (panel.newDetail){
                    console.log('new detail')
                    if (curRule.get(panel.type)){
                        curRule.get(panel.type).add(panel.model);
                    } else {
                        var model = new Backbone.Collection();

                        model.add(panel.model);
                        curRule.set(panel.type, model);

                    }
                    curRule.set({detID: curRule.get('detID') + 1}, {silent:true})
                    panel.model.set({did: curRule.get('detID')});

                    console.log("assigned id", curRule)
                }
               $('#detail-modal').modal('hide');
               curRule.needsSave = true;
            curRule.trigger("needsSave")
            }
            $('.cancel-edit-button', this.$el)[0].onclick = function(){
                $('#detail-modal').modal('hide');
            }

        },
        fillTemplate: function(){
            var inputs = $('.detail-input');
             for (var i=0;i<inputs.length;i++){
                    var cur = inputs[i];
                    cur.value = this.model.get(cur.name);

                }
        }






    });


    return DetailEditor;

});
