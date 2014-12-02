({
    mainConfigFile: '../www_modular/js/main.js',
    baseUrl: '../www_modular/ace/assets/js',
    name: 'ace',
    out: '../www_modular/js/ace.js',
    removeCombined: true,
    findNestedDependencies: true,
    generateSourceMaps: true,
    preserveLicenseComments: false,
    optimize: 'uglify2',
    paths: {
        'jsplumb': 'empty:',
        'bootstrap': 'empty:',
        'jquery': 'empty:',
        'jquery_ui': 'empty:',
        'underscore': 'empty:',
        'backbone': 'empty:',
        'ckeditor': 'empty:',
        'amcharts': 'empty:',
        'bootstrapswitch': 'empty:',
        '/services/recaptcha': 'empty:'
    },
    shim: {
        bootstrap: {
            deps: ['jquery']
        },
        jsplumb: {
            deps: ['jquery', 'jquery_ui']
        },
        fullCalendar: {
            deps: ['jquery', 'moment', 'jquery_ui']
        },
        jquery_ui: {
            deps: ['jquery'],
        },
        amchartspie: { deps: ['amcharts'], exports: 'AmCharts', init: function () {
            AmCharts.isReady = true;
        }},
        amchartsserial: { deps: ['amcharts'], exports: 'AmCharts', init: function () {
            AmCharts.isReady = true;
        }},
        amchartslight: { deps: ['amcharts'], exports: 'AmCharts', init: function () {
            AmCharts.isReady = true;
        }},
    },
    inlineText: true,
    exclude: [

    ],
    include: [
        'ace-extra.js',
        'ace-elements.js',
        'ace.js',
        'jquery-ui.custom.js',
        'jquery.ui.touch-punch.js',
        'jquery.easypiechart.js',
        'jquery.sparkline.js',
        'flot/jquery.flot.js',
        'flot/jquery.flot.pie.js',
        'flot/jquery.flot.resize.js',
        'ace/elements.scroller.js',
        'ace/elements.colorpicker.js',
        'ace/elements.fileinput.js',
        'ace/elements.typeahead.js',
        'ace/elements.wysiwyg.js',
        'ace/elements.spinner.js',
        'ace/elements.treeview.js',
        'ace/elements.wizard.js',
        'ace/elements.aside.js',
        'ace/ace.js',
        'ace/ace.ajax-content.js',
        'ace/ace.touch-drag.js',
        'ace/ace.sidebar.js',
        'ace/ace.sidebar-scroll-1.js',
        'ace/ace.submenu-hover.js',
        'ace/ace.widget-box.js',
        'ace/ace.settings.js',
        'ace/ace.settings-rtl.js',
        'ace/ace.settings-skin.js',
        'ace/ace.widget-on-reload.js',
        'ace/ace.searchbox-autocomplete.js'

    ]
})
