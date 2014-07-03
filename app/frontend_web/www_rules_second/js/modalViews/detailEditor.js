
define([
    // These are path alias that we configured in our main.js
    'jquery',     // lib/jquery/jquery
    'underscore', // lib/underscore/underscore
    'backbone',    // lib/backbone/backbone
    'internalViews/detailSearchBox',
    'internalViews/multiSelectSearch',
    'models/ruleModel'


], function ($, _, Backbone,  detailSearchBox, multiSelectSearch, curRule) {

    var DetailEditor = Backbone.View.extend({


        initialize: function(param){
            console.log(param);
            this.model = param.model;
            this.newDetail = param.newDetail
            this.$el = param.el;
            this.template = param.template
            this.type = param.type;
            this.$el.html(this.template());
            var searchEl = $('.search', this.$el)
            if (searchEl.length!=0){
                var anon =  Backbone.Collection.extend( {url: '/search'})
                var searchBox = new detailSearchBox({collection: new anon(), type: this.type, el: searchEl})
                searchBox.render();
            }
            var multiSearchEl = $('.multi-select-search', this.$el)
            console.log("multiEls", multiSearchEl)
            $.each(multiSearchEl, function(a, cur){
                console.log('cur', cur)
                var anon =  Backbone.Collection.extend( {url: '/search'})
                var searchBox = new multiSelectSearch({avail: new anon(), type: cur.getAttribute("type"), el: multiSearchEl, selected: new Backbone.Collection})
            })

            if (!this.newDetail){
                this.fillTemplate();
            }
            this.$el.show();


            var panel = this;
            $('.confirm-detail-button', this.$el)[0].onclick = function(){
                var inputs = $('.detail-input');
                for (var i=0;i<inputs.length;i++){
                    var cur = inputs[i];
                    panel.model.set(cur.name, cur.value);

                }
                var multi = $('.multi-select-search', this.$el)
                _.each(multi, function(cur){
                    var selectedItems = $('.selected-items option', cur)
                    console.log('selected box is ', selectedItems)
                    var idList = [];
                    _.each(selectedItems, function(cur){
                        idList.push(cur.value)
                    })
                    console.log("cur", cur.getAttribute('name'))
                    panel.model.set(cur.getAttribute('name'), idList);
                    console.log(panel.model)
                }, this)
                console.log(panel.model)
                if (panel.newDetail){
                    if (curRule.get(panel.type)){
                        curRule.get(panel.type).add(panel.model);
                    } else {
                        var model = new Backbone.Collection();
                        model.add(panel.model);
                        curRule.set(panel.type, model);

                    }
                    console.log(curRule)
                    curRule.save()
                }
               $('#detail-modal').modal('hide');


            }

            $('.cancel-edit-button', this.$el)[0].onclick = function(){

                $('#detail-modal').modal('hide');

            }
        },
        fillTemplate: function(){
            var inputs = $('.detail-input');
             for (var i=0;i<inputs.length;i++){
                    var cur = inputs[i];
                    console.log(cur);
                    cur.value =this.model.get(cur.name);

                }
        }






    });


    return DetailEditor;

});
