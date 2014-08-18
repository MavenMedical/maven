/**
 * Created by Asmaa Aljuhani on 8/8/14.
 */

define([
    // These are path alias that we configured in our main.js
    'jquery',     // lib/jquery/jquery
    'underscore', // lib/underscore/underscore
    'backbone',    // lib/backbone/backbone
    'jsplumb',
    'globalmodels/contextModel'
], function ($, _, Backbone, jsPlumb, contextModel) {
    var Pathway = Backbone.View.extend({
        initialize: function (arg) {
            _.bindAll(this, 'render', 'drawTree', 'showFirstchild', 'expandAll', 'suggested');

            this.template = _.template(arg.template);
            this.$el.html(this.template());
            console.log('pathway ini');
            //$('#content').css("width", "80%");

            // this.render();
            setTimeout(_.bind(this.showFirstchild, this), 1000);

            $('span[data-toggle="tooltip"]').tooltip({
                animated: 'fade',
                placement: 'left',
                container: 'body'
            });


            jsPlumb.importDefaults({
                container: '#pathway-container',
                MaxConnections: -1,
                Endpoint: 'Blank',
                PaintStyle: {
                    lineWidth: 2,
                    strokeStyle: '#ccc'
                },
                HoverPaintStyle: {
                    lineWidth: 3,
                    strokeStyle: '#61B7CF'
                },
                DragOptions: { cursor: "crosshair" },
                Endpoints: [
                    [ "Dot", { radius: 1 } ],
                    [ "Dot", { radius: 1 } ]
                ],
                EndpointStyles: [
                    { fillStyle: "#ccc" },
                    { fillStyle: "#ccc" }
                ],
                Connector: [ "Flowchart", {
                    cornerRadius: 3
                }],
                Anchors: [ "Bottom", "Top" ]
                /* ConnectionOverlays: [
                 [ "Arrow", { location: 2 } ],
                 [ "Label", {
                 location: 0.1,
                 id: "label",
                 cssClass: "aLabel"
                 }]
                 ]*/

            });

            $('#pathway-container').draggable();

            /*
             $('#pathway-container').on('wheel', function(data){
             data.preventDefault()
             var re = /scale\((.*)\)/
             var n = that.treeEl[0].style.transform
             var result = re.exec(n)
             if (data.originalEvent.deltaY > 0){
             var newScale = result[1] -.05
             } else {
             var newScale = (result[1]-0) + .05

             }
             var scaleString = 'scale(' + newScale +')'
             that.treeEl.css({'transform': scaleString})

             })

             */
        },
        events: {
            'click button#copybutton': 'copyIndex',
            'click .qualifier': 'toggleChildren',
            'click button#expandAll': 'expandAll',
            'click button#sugPath': 'suggested'

        },
        render: function () {


        },
        copyIndex: function () {

            $('<div>').attr('id', 'copiedText').appendTo('body');


            //window.prompt ("Copy to clipboard: Ctrl+C, Enter", "test copy");
            $('#copiedText').text("In summary, the patient is a 54-year-old man with " +
                "symptomatic mCRPC and good performance status (ECOG 0-1) " +
                "who has not received prior docetaxel therapy. " +
                "\r\n" +
                "   - This is evidenced by rising PSA in the setting of castrate testosterone levels." +
                "\r\n" +
                "   - Prior radiographic imaging has confirmed metastasis." +
                "\r\n" +
                "   - Symptoms that are attributable to the metastatic disease" +
                "burden include:" +
                "\r\n" +
                "    [[[SYMPTOMS]]]" +
                "\r\n" +
                "Management Plan:" +
                "\r\n" +
                "Per AUA guidelines*, The patient will receive" +
                "\r\n" +
                "   - Docetaxel therapy" +
                "\r\n" +
                "   - Abiraterone + prednisone" +
                "\r\n" +
                "   [[[OR Since the patient cannot receive the standard" +
                "tretatment, he was offered ketoconazole + steroid," +
                "mitoxantrone or radionuclide therapy]]]" +
                "\r\n \r\n" +
                "*Index Patient 3 - http://www.auanet.org/education/guidelines/castration-resistant-prostate-cancer.cfm");


            $('#toast').css('visibility', 'visible');

            setTimeout(function () {

                $("#toast").fadeOut("slow", function () {
                    //$('#toast').css('visibility', 'hidden');
                });

            }, 2000);

        },
        toggleChildren: function (self) {
            var parent = (self.currentTarget.parentNode)
            $('.children', parent).first().toggle();
            this.drawTree();
        },
        drawTree: function () {
            jsPlumb.reset();


            var nodeList = $('.qualifier');
            $.each(nodeList, function (key, value) {
                var s = jsPlumb.addEndpoint(value, {anchor: 'Bottom'});
                var parent = (value.parentNode);
                var child = $('.children', parent).first();
                if (child[0]) {
                    var children = child[0].children;
                    $.each(children, function (key2, value2) {
                        var targetDiv = $('.qualifier', value2).first(); //top endpiont
                        var t = jsPlumb.addEndpoint(targetDiv, {anchor: 'Top'})
                        if (($(value).is(":visible")) && ($(targetDiv).is(":visible"))) {
                            jsPlumb.connect({source: s, target: t});
                        }
                    })


                }
            })

            if (($('#gp').is(":visible")) && ($('#i3').is(":visible"))) {
                var s = jsPlumb.addEndpoint($('#gp'), {anchor: 'Bottom'});
                var t = jsPlumb.addEndpoint($('#i3'), {anchor: 'Top'});
                jsPlumb.connect({source: s, target: t});
            }
        },
        showFirstchild: function () {
            $('#n1').click();
        },
        suggested: function () {
            console.log('suggested');
            $('#n1').click();
            $('.children').toggle();
            this.drawTree();

            $('.suggested').css({
                "border": "2px solid orange"
            })
        },
        expandAll: function () {
            console.log('expandAll');
            $('#n1').click();
            $('.children').toggle();
            this.drawTree();


            $("#pathway-container").css({
                "-webkit-transform": "scale(0.75)",
                "-moz-transform": "scale(0.75)",
                "-ms-transform": "scale(0.75)",
                "-o-transform": "scale(0.75)",
                "transform": "scale(0.75)"
            });
        }
    });
    return Pathway;
});