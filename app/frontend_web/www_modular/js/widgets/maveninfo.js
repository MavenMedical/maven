/**
 * Created by Asmaa Aljuhani on 8/8/14.
 */

define([
    // These are path alias that we configured in our main.js
    'jquery',     // lib/jquery/jquery
    'underscore', // lib/underscore/underscore
    'backbone',    // lib/backbone/backbone
    'globalmodels/contextModel',
    'pathway/models/treeModel'
], function ($, _, Backbone, contextModel, curTree) {
    var MavenInfo = Backbone.View.extend({

            initialize: function (arg) {
                this.template = _.template(arg.template);
                    curTree.on('propagate', this.render, this);
                    contextModel.on('change:page change:pathid', this.hidePopup , this);
                this.dynamicLayout = true;

            },
            test: function(){
              console.log("hi there test");
            },
            showhide: function () {
                this.$el.show();
            },
            events: {
                'click button.close': 'hidePopup',
                'click #toggleLayout': 'toggleLayout'

            },
            render: function () {
                if (!curTree.get('selectedNode')){
		    this.hidePopup()
                    return
                }
		if(curTree.get('selectedNode') == this.selectedNode) {return}

                console.log('selectedNode', curTree.get('selectedNode'));
                // for accounts with no pathways
                if(typeof curTree.get('selectedNode') !== 'undefined') {

                    var that = this;
                    // Don't show if there is no text or if selected node is Protocol
                    if (curTree.get('selectedNode').attributes.sidePanelText && !curTree.get('selectedNode').attributes.isProtocol ) {
                       this.hidePopup();
                       // this.$el.hide(); // hide previous side-popup
                        this.selectedNode = curTree.get('selectedNode');
                        this.$el.html(this.template(curTree.get('selectedNode').attributes));
                        this.showPopup();

                    } else {this.hidePopup();}
                } else {this.hidePopup()}
                //         return this;
            },
            hidePopup: function () {
                this.$el.hide();
                this.selectedNode = curTree.get('selectedNode');
            },
            showPopup: function(){
                 if (this.dynamicLayout) {
                            $('#side-popup').css('top', curTree.get('selectedNodeOffset').top);
                            $('#side-popup').css('left', curTree.get('selectedNodeOffset').left + curTree.get('selectedNodeWidth') + 10);
                      $('#side-popup').css('bottom', 'none');
                            $('#side-popup').css('right', 'none');
                        }else{
                            $('#side-popup').css('top', 'none');
                            $('#side-popup').css('left', 'none');
                            $('#side-popup').css('bottom', 5);
                            $('#side-popup').css('right', 5);
                        }

                        this.$el.show(1000);

            },
            toggleLayout: function(){
                console.log('toggle', 'test toggle');
                if (this.dynamicLayout){
                    this.dynamicLayout = false;
                }else{
                    this.dynamicLayout = true;
                }
                this.showPopup();
            }
        })
        ;
    return MavenInfo;
})
;
