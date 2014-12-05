require([
    "ace/assets/js/ace-extra.js",
//    "ace/assets/js/html5shiv.js",
//    "ace/assets/js/respond.js",
//    "ace/assets/js/jquery.js",
    "ace/assets/js/jquery1x.js",
    "ace/assets/js/jquery.mobile.custom.js",
    "ace/assets/js/bootstrap.js",
    "ace/assets/js/excanvas.js",
    "ace/assets/js/ace-elements.js",
    "ace/assets/js/ace.js",
    "ace/assets/js/jquery-ui.custom.js",
    "ace/assets/js/jquery.ui.touch-punch.js",
    "ace/assets/js/jquery.easypiechart.js",
    "ace/assets/js/jquery.sparkline.js",
    "ace/assets/js/flot/jquery.flot.js",
    "ace/assets/js/flot/jquery.flot.pie.js",
    "ace/assets/js/flot/jquery.flot.resize.js",
    "ace/assets/js/ace/elements.scroller.js",
    "ace/assets/js/ace/elements.colorpicker.js",
    "ace/assets/js/ace/elements.fileinput.js",
    "ace/assets/js/ace/elements.typeahead.js",
    "ace/assets/js/ace/elements.wysiwyg.js",
    "ace/assets/js/ace/elements.spinner.js",
    "ace/assets/js/ace/elements.treeview.js",
    "ace/assets/js/ace/elements.wizard.js",
    "ace/assets/js/ace/elements.aside.js",
    "ace/assets/js/ace/ace.js",
    "ace/assets/js/ace/ace.ajax-content.js",
    "ace/assets/js/ace/ace.touch-drag.js",
    "ace/assets/js/ace/ace.sidebar.js",
    "ace/assets/js/ace/ace.sidebar-scroll-1.js",
    "ace/assets/js/ace/ace.submenu-hover.js",
    "ace/assets/js/ace/ace.widget-box.js",
    "ace/assets/js/ace/ace.settings.js",
    "ace/assets/js/ace/ace.settings-rtl.js",
    "ace/assets/js/ace/ace.settings-skin.js",
    "ace/assets/js/ace/ace.widget-on-reload.js",
    "ace/assets/js/ace/ace.searchbox-autocomplete.js"
], function() {
    try {
        console.log('loaded ace settings')
        ace.settings.check('breadcrumbs', 'fixed')
    } catch (e) {
    }
})
