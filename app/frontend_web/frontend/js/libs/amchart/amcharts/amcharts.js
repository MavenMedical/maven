if (!AmCharts)var AmCharts = {themes: {}, maps: {}, inheriting: {}, charts: [], onReadyArray: [], useUTC: !1, updateRate: 40, uid: 0};
AmCharts.Class = function (a) {
    var b = function () {
        arguments[0] !== AmCharts.inheriting && (this.events = {}, this.construct.apply(this, arguments))
    };
    a.inherits ? (b.prototype = new a.inherits(AmCharts.inheriting), b.base = a.inherits.prototype, delete a.inherits) : (b.prototype.createEvents = function () {
        for (var a = 0, b = arguments.length; a < b; a++)this.events[arguments[a]] = []
    }, b.prototype.listenTo = function (a, b, c) {
        this.removeListener(a, b, c);
        a.events[b].push({handler: c, scope: this})
    }, b.prototype.addListener = function (a, b, c) {
        this.removeListener(this,
            a, b);
        this.events[a].push({handler: b, scope: c})
    }, b.prototype.removeListener = function (a, b, c) {
        if (a && a.events)for (a = a.events[b], b = a.length - 1; 0 <= b; b--)a[b].handler === c && a.splice(b, 1)
    }, b.prototype.fire = function (a, b) {
        for (var c = this.events[a], g = 0, h = c.length; g < h; g++) {
            var k = c[g];
            k.handler.call(k.scope, b)
        }
    });
    for (var c in a)b.prototype[c] = a[c];
    return b
};
AmCharts.addChart = function (a) {
    AmCharts.charts.push(a)
};
AmCharts.removeChart = function (a) {
    for (var b = AmCharts.charts, c = b.length - 1; 0 <= c; c--)b[c] == a && b.splice(c, 1)
};
AmCharts.IEversion = 0;
AmCharts.isModern = !0;
AmCharts.navigator = navigator.userAgent.toLowerCase();
-1 != AmCharts.navigator.indexOf("msie") && (AmCharts.IEversion = parseInt(AmCharts.navigator.split("msie")[1]), document.documentMode && (AmCharts.IEversion = Number(document.documentMode)), 9 > AmCharts.IEversion && (AmCharts.isModern = !1));
AmCharts.dx = 0;
AmCharts.dy = 0;
if (document.addEventListener || window.opera)AmCharts.isNN = !0, AmCharts.isIE = !1, AmCharts.dx = 0.5, AmCharts.dy = 0.5;
document.attachEvent && (AmCharts.isNN = !1, AmCharts.isIE = !0, AmCharts.isModern || (AmCharts.dx = 0, AmCharts.dy = 0));
window.chrome && (AmCharts.chrome = !0);
AmCharts.handleResize = function () {
    for (var a = AmCharts.charts, b = 0; b < a.length; b++) {
        var c = a[b];
        c && c.div && c.handleResize()
    }
};
AmCharts.handleMouseUp = function (a) {
    for (var b = AmCharts.charts, c = 0; c < b.length; c++) {
        var d = b[c];
        d && d.handleReleaseOutside(a)
    }
};
AmCharts.handleMouseMove = function (a) {
    for (var b = AmCharts.charts, c = 0; c < b.length; c++) {
        var d = b[c];
        d && d.handleMouseMove(a)
    }
};
AmCharts.resetMouseOver = function () {
    for (var a = AmCharts.charts, b = 0; b < a.length; b++) {
        var c = a[b];
        c && (c.mouseIsOver = !1)
    }
};
AmCharts.ready = function (a) {
    AmCharts.onReadyArray.push(a)
};
AmCharts.handleLoad = function () {
    AmCharts.isReady = !0;
    for (var a = AmCharts.onReadyArray, b = 0; b < a.length; b++) {
        var c = a[b];
        isNaN(AmCharts.processDelay) ? c() : setTimeout(c, AmCharts.processDelay * b)
    }
};
AmCharts.getUniqueId = function () {
    AmCharts.uid++;
    return"AmChartsEl-" + AmCharts.uid
};
AmCharts.isNN && (document.addEventListener("mousemove", AmCharts.handleMouseMove, !0), window.addEventListener("resize", AmCharts.handleResize, !0), document.addEventListener("mouseup", AmCharts.handleMouseUp, !0), window.addEventListener("load", AmCharts.handleLoad, !0));
AmCharts.isIE && (document.attachEvent("onmousemove", AmCharts.handleMouseMove), window.attachEvent("onresize", AmCharts.handleResize), document.attachEvent("onmouseup", AmCharts.handleMouseUp), window.attachEvent("onload", AmCharts.handleLoad));
AmCharts.clear = function () {
    var a = AmCharts.charts;
    if (a)for (var b = 0; b < a.length; b++)a[b].clear();
    AmCharts.charts = null;
    AmCharts.isNN && (document.removeEventListener("mousemove", AmCharts.handleMouseMove, !0), window.removeEventListener("resize", AmCharts.handleResize, !0), document.removeEventListener("mouseup", AmCharts.handleMouseUp, !0), window.removeEventListener("load", AmCharts.handleLoad, !0));
    AmCharts.isIE && (document.detachEvent("onmousemove", AmCharts.handleMouseMove), window.detachEvent("onresize", AmCharts.handleResize),
        document.detachEvent("onmouseup", AmCharts.handleMouseUp), window.detachEvent("onload", AmCharts.handleLoad))
};
AmCharts.makeChart = function (a, b, c) {
    var d = b.type, f = b.theme;
    AmCharts.isString(f) && (f = AmCharts.themes[f], b.theme = f);
    var e;
    switch (d) {
        case "serial":
            e = new AmCharts.AmSerialChart(f);
            break;
        case "xy":
            e = new AmCharts.AmXYChart(f);
            break;
        case "pie":
            e = new AmCharts.AmPieChart(f);
            break;
        case "radar":
            e = new AmCharts.AmRadarChart(f);
            break;
        case "gauge":
            e = new AmCharts.AmAngularGauge(f);
            break;
        case "funnel":
            e = new AmCharts.AmFunnelChart(f);
            break;
        case "map":
            e = new AmCharts.AmMap(f);
            break;
        case "stock":
            e = new AmCharts.AmStockChart(f)
    }
    AmCharts.extend(e,
        b);
    AmCharts.isReady ? isNaN(c) ? e.write(a) : setTimeout(function () {
        AmCharts.realWrite(e, a)
    }, c) : AmCharts.ready(function () {
        isNaN(c) ? e.write(a) : setTimeout(function () {
            AmCharts.realWrite(e, a)
        }, c)
    });
    return e
};
AmCharts.realWrite = function (a, b) {
    a.write(b)
};
AmCharts.toBoolean = function (a, b) {
    if (void 0 === a)return b;
    switch (String(a).toLowerCase()) {
        case "true":
        case "yes":
        case "1":
            return!0;
        case "false":
        case "no":
        case "0":
        case null:
            return!1;
        default:
            return Boolean(a)
    }
};
AmCharts.removeFromArray = function (a, b) {
    var c;
    for (c = a.length - 1; 0 <= c; c--)a[c] == b && a.splice(c, 1)
};
AmCharts.getDecimals = function (a) {
    var b = 0;
    isNaN(a) || (a = String(a), -1 != a.indexOf("e-") ? b = Number(a.split("-")[1]) : -1 != a.indexOf(".") && (b = a.split(".")[1].length));
    return b
};
AmCharts.wrappedText = function (a, b, c, d, f, e, g, h, k) {
    var l = AmCharts.text(a, b, c, d, f, e, g), m = "\n";
    AmCharts.isModern || (m = "<br>");
    if (10 < k)return l;
    if (l) {
        var p = l.getBBox();
        if (p.width > h) {
            l.remove();
            for (var l = [], n = 0; -1 < (index = b.indexOf(" ", n));)l.push(index), n = index + 1;
            for (var q = Math.round(b.length / 2), s = 1E3, r, n = 0; n < l.length; n++) {
                var u = Math.abs(l[n] - q);
                u < s && (r = l[n], s = u)
            }
            if (isNaN(r)) {
                h = Math.ceil(p.width / h);
                for (n = 1; n < h; n++)r = Math.round(b.length / h * n), b = b.substr(0, r) + m + b.substr(r);
                return AmCharts.text(a, b, c, d, f, e,
                    g)
            }
            b = b.substr(0, r) + m + b.substr(r + 1);
            return AmCharts.wrappedText(a, b, c, d, f, e, g, h, k + 1)
        }
        return l
    }
};
AmCharts.getStyle = function (a, b) {
    var c = "";
    document.defaultView && document.defaultView.getComputedStyle ? c = document.defaultView.getComputedStyle(a, "").getPropertyValue(b) : a.currentStyle && (b = b.replace(/\-(\w)/g, function (a, b) {
        return b.toUpperCase()
    }), c = a.currentStyle[b]);
    return c
};
AmCharts.removePx = function (a) {
    return Number(a.substring(0, a.length - 2))
};
AmCharts.getURL = function (a, b) {
    if (a)if ("_self" != b && b)if ("_top" == b && window.top)window.top.location.href = a; else if ("_parent" == b && window.parent)window.parent.location.href = a; else {
        var c = document.getElementsByName(b)[0];
        c ? c.src = a : window.open(a)
    } else window.location.href = a
};
AmCharts.ifArray = function (a) {
    return a && 0 < a.length ? !0 : !1
};
AmCharts.callMethod = function (a, b) {
    var c;
    for (c = 0; c < b.length; c++) {
        var d = b[c];
        if (d) {
            if (d[a])d[a]();
            var f = d.length;
            if (0 < f) {
                var e;
                for (e = 0; e < f; e++) {
                    var g = d[e];
                    if (g && g[a])g[a]()
                }
            }
        }
    }
};
AmCharts.toNumber = function (a) {
    return"number" == typeof a ? a : Number(String(a).replace(/[^0-9\-.]+/g, ""))
};
AmCharts.toColor = function (a) {
    if ("" !== a && void 0 !== a)if (-1 != a.indexOf(",")) {
        a = a.split(",");
        var b;
        for (b = 0; b < a.length; b++) {
            var c = a[b].substring(a[b].length - 6, a[b].length);
            a[b] = "#" + c
        }
    } else a = a.substring(a.length - 6, a.length), a = "#" + a;
    return a
};
AmCharts.toCoordinate = function (a, b, c) {
    var d;
    void 0 !== a && (a = String(a), c && c < b && (b = c), d = Number(a), -1 != a.indexOf("!") && (d = b - Number(a.substr(1))), -1 != a.indexOf("%") && (d = b * Number(a.substr(0, a.length - 1)) / 100));
    return d
};
AmCharts.fitToBounds = function (a, b, c) {
    a < b && (a = b);
    a > c && (a = c);
    return a
};
AmCharts.isDefined = function (a) {
    return void 0 === a ? !1 : !0
};
AmCharts.stripNumbers = function (a) {
    return a.replace(/[0-9]+/g, "")
};
AmCharts.roundTo = function (a, b) {
    if (0 > b)return a;
    var c = Math.pow(10, b);
    return Math.round(a * c) / c
};
AmCharts.toFixed = function (a, b) {
    var c = String(Math.round(a * Math.pow(10, b)));
    if (0 < b) {
        var d = c.length;
        if (d < b) {
            var f;
            for (f = 0; f < b - d; f++)c = "0" + c
        }
        d = c.substring(0, c.length - b);
        "" === d && (d = 0);
        return d + "." + c.substring(c.length - b, c.length)
    }
    return String(c)
};
AmCharts.formatDuration = function (a, b, c, d, f, e) {
    var g = AmCharts.intervals, h = e.decimalSeparator;
    if (a >= g[b].contains) {
        var k = a - Math.floor(a / g[b].contains) * g[b].contains;
        "ss" == b && (k = AmCharts.formatNumber(k, e), 1 == k.split(h)[0].length && (k = "0" + k));
        ("mm" == b || "hh" == b) && 10 > k && (k = "0" + k);
        c = k + "" + d[b] + "" + c;
        a = Math.floor(a / g[b].contains);
        b = g[b].nextInterval;
        return AmCharts.formatDuration(a, b, c, d, f, e)
    }
    "ss" == b && (a = AmCharts.formatNumber(a, e), 1 == a.split(h)[0].length && (a = "0" + a));
    ("mm" == b || "hh" == b) && 10 > a && (a = "0" + a);
    c = a + "" +
        d[b] + "" + c;
    if (g[f].count > g[b].count)for (a = g[b].count; a < g[f].count; a++)b = g[b].nextInterval, "ss" == b || "mm" == b || "hh" == b ? c = "00" + d[b] + "" + c : "DD" == b && (c = "0" + d[b] + "" + c);
    ":" == c.charAt(c.length - 1) && (c = c.substring(0, c.length - 1));
    return c
};
AmCharts.formatNumber = function (a, b, c, d, f) {
    a = AmCharts.roundTo(a, b.precision);
    isNaN(c) && (c = b.precision);
    var e = b.decimalSeparator;
    b = b.thousandsSeparator;
    var g;
    g = 0 > a ? "-" : "";
    a = Math.abs(a);
    var h = String(a), k = !1;
    -1 != h.indexOf("e") && (k = !0);
    0 <= c && !k && (h = AmCharts.toFixed(a, c));
    var l = "";
    if (k)l = h; else {
        var h = h.split("."), k = String(h[0]), m;
        for (m = k.length; 0 <= m; m -= 3)l = m != k.length ? 0 !== m ? k.substring(m - 3, m) + b + l : k.substring(m - 3, m) + l : k.substring(m - 3, m);
        void 0 !== h[1] && (l = l + e + h[1]);
        void 0 !== c && 0 < c && "0" != l && (l = AmCharts.addZeroes(l,
            e, c))
    }
    l = g + l;
    "" === g && !0 === d && 0 !== a && (l = "+" + l);
    !0 === f && (l += "%");
    return l
};
AmCharts.addZeroes = function (a, b, c) {
    a = a.split(b);
    void 0 === a[1] && 0 < c && (a[1] = "0");
    return a[1].length < c ? (a[1] += "0", AmCharts.addZeroes(a[0] + b + a[1], b, c)) : void 0 !== a[1] ? a[0] + b + a[1] : a[0]
};
AmCharts.scientificToNormal = function (a) {
    var b;
    a = String(a).split("e");
    var c;
    if ("-" == a[1].substr(0, 1)) {
        b = "0.";
        for (c = 0; c < Math.abs(Number(a[1])) - 1; c++)b += "0";
        b += a[0].split(".").join("")
    } else {
        var d = 0;
        b = a[0].split(".");
        b[1] && (d = b[1].length);
        b = a[0].split(".").join("");
        for (c = 0; c < Math.abs(Number(a[1])) - d; c++)b += "0"
    }
    return b
};
AmCharts.toScientific = function (a, b) {
    if (0 === a)return"0";
    var c = Math.floor(Math.log(Math.abs(a)) * Math.LOG10E);
    Math.pow(10, c);
    mantissa = String(mantissa).split(".").join(b);
    return String(mantissa) + "e" + c
};
AmCharts.randomColor = function () {
    return"#" + ("00000" + (16777216 * Math.random() << 0).toString(16)).substr(-6)
};
AmCharts.hitTest = function (a, b, c) {
    var d = !1, f = a.x, e = a.x + a.width, g = a.y, h = a.y + a.height, k = AmCharts.isInRectangle;
    d || (d = k(f, g, b));
    d || (d = k(f, h, b));
    d || (d = k(e, g, b));
    d || (d = k(e, h, b));
    d || !0 === c || (d = AmCharts.hitTest(b, a, !0));
    return d
};
AmCharts.isInRectangle = function (a, b, c) {
    return a >= c.x - 5 && a <= c.x + c.width + 5 && b >= c.y - 5 && b <= c.y + c.height + 5 ? !0 : !1
};
AmCharts.isPercents = function (a) {
    if (-1 != String(a).indexOf("%"))return!0
};
AmCharts.findPosX = function (a) {
    var b = a, c = a.offsetLeft;
    if (a.offsetParent) {
        for (; a = a.offsetParent;)c += a.offsetLeft;
        for (; (b = b.parentNode) && b != document.body;)c -= b.scrollLeft || 0
    }
    return c
};
AmCharts.findPosY = function (a) {
    var b = a, c = a.offsetTop;
    if (a.offsetParent) {
        for (; a = a.offsetParent;)c += a.offsetTop;
        for (; (b = b.parentNode) && b != document.body;)c -= b.scrollTop || 0
    }
    return c
};
AmCharts.findIfFixed = function (a) {
    if (a.offsetParent)for (; a = a.offsetParent;)if ("fixed" == AmCharts.getStyle(a, "position"))return!0;
    return!1
};
AmCharts.findIfAuto = function (a) {
    return a.style && "auto" == AmCharts.getStyle(a, "overflow") ? !0 : a.parentNode ? AmCharts.findIfAuto(a.parentNode) : !1
};
AmCharts.findScrollLeft = function (a, b) {
    a.scrollLeft && (b += a.scrollLeft);
    return a.parentNode ? AmCharts.findScrollLeft(a.parentNode, b) : b
};
AmCharts.findScrollTop = function (a, b) {
    a.scrollTop && (b += a.scrollTop);
    return a.parentNode ? AmCharts.findScrollTop(a.parentNode, b) : b
};
AmCharts.formatValue = function (a, b, c, d, f, e, g, h) {
    if (b) {
        void 0 === f && (f = "");
        var k;
        for (k = 0; k < c.length; k++) {
            var l = c[k], m = b[l];
            void 0 !== m && (m = e ? AmCharts.addPrefix(m, h, g, d) : AmCharts.formatNumber(m, d), a = a.replace(RegExp("\\[\\[" + f + "" + l + "\\]\\]", "g"), m))
        }
    }
    return a
};
AmCharts.formatDataContextValue = function (a, b) {
    if (a) {
        var c = a.match(/\[\[.*?\]\]/g), d;
        for (d = 0; d < c.length; d++) {
            var f = c[d], f = f.substr(2, f.length - 4);
            void 0 !== b[f] && (a = a.replace(RegExp("\\[\\[" + f + "\\]\\]", "g"), b[f]))
        }
    }
    return a
};
AmCharts.massReplace = function (a, b) {
    for (var c in b)if (b.hasOwnProperty(c)) {
        var d = b[c];
        void 0 === d && (d = "");
        a = a.replace(c, d)
    }
    return a
};
AmCharts.cleanFromEmpty = function (a) {
    return a.replace(/\[\[[^\]]*\]\]/g, "")
};
AmCharts.addPrefix = function (a, b, c, d, f) {
    var e = AmCharts.formatNumber(a, d), g = "", h, k, l;
    if (0 === a)return"0";
    0 > a && (g = "-");
    a = Math.abs(a);
    if (1 < a)for (h = b.length - 1; -1 < h; h--) {
        if (a >= b[h].number && (k = a / b[h].number, l = Number(d.precision), 1 > l && (l = 1), c = AmCharts.roundTo(k, l), l = AmCharts.formatNumber(c, {precision: -1, decimalSeparator: d.decimalSeparator, thousandsSeparator: d.thousandsSeparator}), !f || k == c)) {
            e = g + "" + l + "" + b[h].prefix;
            break
        }
    } else for (h = 0; h < c.length; h++)if (a <= c[h].number) {
        k = a / c[h].number;
        l = Math.abs(Math.round(Math.log(k) *
            Math.LOG10E));
        k = AmCharts.roundTo(k, l);
        e = g + "" + k + "" + c[h].prefix;
        break
    }
    return e
};
AmCharts.remove = function (a) {
    a && a.remove()
};
AmCharts.recommended = function () {
    var a = "js";
    document.implementation.hasFeature("http://www.w3.org/TR/SVG11/feature#BasicStructure", "1.1") || swfobject && swfobject.hasFlashPlayerVersion("8") && (a = "flash");
    return a
};
AmCharts.getEffect = function (a) {
    ">" == a && (a = "easeOutSine");
    "<" == a && (a = "easeInSine");
    "elastic" == a && (a = "easeOutElastic");
    return a
};
AmCharts.getObjById = function (a, b) {
    var c, d;
    for (d = 0; d < a.length; d++) {
        var f = a[d];
        f.id == b && (c = f)
    }
    return c
};
AmCharts.applyTheme = function (a, b, c) {
    b || (b = AmCharts.theme);
    b && b[c] && AmCharts.extend(a, b[c])
};
AmCharts.isString = function (a) {
    return"string" == typeof a ? !0 : !1
};
AmCharts.extend = function (a, b, c) {
    for (var d in b)c ? a.hasOwnProperty(d) || (a[d] = b[d]) : a[d] = b[d];
    return a
};
AmCharts.copyProperties = function (a, b) {
    for (var c in a)a.hasOwnProperty(c) && "events" != c && void 0 !== a[c] && "function" != typeof a[c] && "cname" != c && (b[c] = a[c])
};
AmCharts.processObject = function (a, b, c) {
    !1 === a instanceof b && (a = AmCharts.extend(new b(c), a));
    return a
};
AmCharts.fixNewLines = function (a) {
    var b = RegExp("\\n", "g");
    a && (a = a.replace(b, "<br />"));
    return a
};
AmCharts.fixBrakes = function (a) {
    if (AmCharts.isModern) {
        var b = RegExp("<br>", "g");
        a && (a = a.replace(b, "\n"))
    } else a = AmCharts.fixNewLines(a);
    return a
};
AmCharts.deleteObject = function (a, b) {
    if (a) {
        if (void 0 === b || null === b)b = 20;
        if (0 !== b)if ("[object Array]" === Object.prototype.toString.call(a))for (var c = 0; c < a.length; c++)AmCharts.deleteObject(a[c], b - 1), a[c] = null; else if (a && !a.tagName)try {
            for (c in a)a[c] && ("object" == typeof a[c] && AmCharts.deleteObject(a[c], b - 1), "function" != typeof a[c] && (a[c] = null))
        } catch (d) {
        }
    }
};
AmCharts.bounce = function (a, b, c, d, f) {
    return(b /= f) < 1 / 2.75 ? 7.5625 * d * b * b + c : b < 2 / 2.75 ? d * (7.5625 * (b -= 1.5 / 2.75) * b + 0.75) + c : b < 2.5 / 2.75 ? d * (7.5625 * (b -= 2.25 / 2.75) * b + 0.9375) + c : d * (7.5625 * (b -= 2.625 / 2.75) * b + 0.984375) + c
};
AmCharts.easeInSine = function (a, b, c, d, f) {
    return-d * Math.cos(b / f * (Math.PI / 2)) + d + c
};
AmCharts.easeOutSine = function (a, b, c, d, f) {
    return d * Math.sin(b / f * (Math.PI / 2)) + c
};
AmCharts.easeOutElastic = function (a, b, c, d, f) {
    a = 1.70158;
    var e = 0, g = d;
    if (0 === b)return c;
    if (1 == (b /= f))return c + d;
    e || (e = 0.3 * f);
    g < Math.abs(d) ? (g = d, a = e / 4) : a = e / (2 * Math.PI) * Math.asin(d / g);
    return g * Math.pow(2, -10 * b) * Math.sin(2 * (b * f - a) * Math.PI / e) + d + c
};
AmCharts.AxisBase = AmCharts.Class({construct: function (a) {
    this.viY = this.viX = this.y = this.x = this.dy = this.dx = 0;
    this.axisThickness = 1;
    this.axisColor = "#000000";
    this.axisAlpha = 1;
    this.gridCount = this.tickLength = 5;
    this.gridAlpha = 0.15;
    this.gridThickness = 1;
    this.gridColor = "#000000";
    this.dashLength = 0;
    this.labelFrequency = 1;
    this.showLastLabel = this.showFirstLabel = !0;
    this.fillColor = "#FFFFFF";
    this.fillAlpha = 0;
    this.labelsEnabled = !0;
    this.labelRotation = 0;
    this.autoGridCount = !0;
    this.valueRollOverColor = "#CC0000";
    this.offset =
        0;
    this.guides = [];
    this.visible = !0;
    this.counter = 0;
    this.guides = [];
    this.ignoreAxisWidth = this.inside = !1;
    this.minHorizontalGap = 75;
    this.minVerticalGap = 35;
    this.titleBold = !0;
    this.minorGridEnabled = !1;
    this.minorGridAlpha = 0.07;
    this.autoWrap = !1;
    this.titleAlign = "middle";
    AmCharts.applyTheme(this, a, "AxisBase")
}, zoom: function (a, b) {
    this.start = a;
    this.end = b;
    this.dataChanged = !0;
    this.draw()
}, fixAxisPosition: function () {
    var a = this.position;
    "H" == this.orientation ? ("left" == a && (a = "bottom"), "right" == a && (a = "top")) : ("bottom" ==
        a && (a = "left"), "top" == a && (a = "right"));
    this.position = a
}, draw: function () {
    var a = this.chart;
    this.allLabels = [];
    this.counter = 0;
    this.destroy();
    this.fixAxisPosition();
    this.labels = [];
    var b = a.container, c = b.set();
    a.gridSet.push(c);
    this.set = c;
    b = b.set();
    a.axesLabelsSet.push(b);
    this.labelsSet = b;
    this.axisLine = new this.axisRenderer(this);
    this.autoGridCount ? ("V" == this.orientation ? (a = this.height / this.minVerticalGap, 3 > a && (a = 3)) : a = this.width / this.minHorizontalGap, this.gridCountR = Math.max(a, 1)) : this.gridCountR = this.gridCount;
    this.axisWidth = this.axisLine.axisWidth;
    this.addTitle()
}, setOrientation: function (a) {
    this.orientation = a ? "H" : "V"
}, addTitle: function () {
    var a = this.title;
    if (a) {
        var b = this.chart, c = this.titleColor;
        void 0 === c && (c = b.color);
        var d = this.titleFontSize;
        isNaN(d) && (d = b.fontSize + 1);
        this.titleLabel = AmCharts.text(b.container, a, c, b.fontFamily, d, this.titleAlign, this.titleBold)
    }
}, positionTitle: function () {
    var a = this.titleLabel;
    if (a) {
        var b, c, d = this.labelsSet, f = {};
        0 < d.length() ? f = d.getBBox() : (f.x = 0, f.y = 0, f.width = this.viW, f.height =
            this.viH);
        d.push(a);
        var d = f.x, e = f.y;
        AmCharts.VML && (this.rotate ? d -= this.x : e -= this.y);
        var g = f.width, f = f.height, h = this.viW, k = this.viH, l = 0, m = a.getBBox().height / 2, p = this.inside, n = this.titleAlign;
        switch (this.position) {
            case "top":
                b = "left" == n ? -1 : "right" == n ? h : h / 2;
                c = e - 10 - m;
                break;
            case "bottom":
                b = "left" == n ? -1 : "right" == n ? h : h / 2;
                c = e + f + 10 + m;
                break;
            case "left":
                b = d - 10 - m;
                p && (b -= 5);
                c = "left" == n ? k + 1 : "right" == n ? -1 : k / 2;
                l = -90;
                break;
            case "right":
                b = d + g + 10 + m - 3, p && (b += 7), c = "left" == n ? k + 2 : "right" == n ? -2 : k / 2, l = -90
        }
        this.marginsChanged ?
            (a.translate(b, c), this.tx = b, this.ty = c) : a.translate(this.tx, this.ty);
        this.marginsChanged = !1;
        0 !== l && a.rotate(l)
    }
}, pushAxisItem: function (a, b) {
    var c = a.graphics();
    0 < c.length() && (b ? this.labelsSet.push(c) : this.set.push(c));
    (c = a.getLabel()) && this.labelsSet.push(c)
}, addGuide: function (a) {
    this.guides.push(a)
}, removeGuide: function (a) {
    var b = this.guides, c;
    for (c = 0; c < b.length; c++)b[c] == a && b.splice(c, 1)
}, handleGuideOver: function (a) {
    clearTimeout(this.chart.hoverInt);
    var b = a.graphics.getBBox(), c = b.x + b.width / 2, b = b.y +
        b.height / 2, d = a.fillColor;
    void 0 === d && (d = a.lineColor);
    this.chart.showBalloon(a.balloonText, d, !0, c, b)
}, handleGuideOut: function (a) {
    this.chart.hideBalloon()
}, addEventListeners: function (a, b) {
    var c = this;
    a.mouseover(function () {
        c.handleGuideOver(b)
    });
    a.mouseout(function () {
        c.handleGuideOut(b)
    })
}, getBBox: function () {
    var a = this.labelsSet.getBBox();
    AmCharts.VML || (a = {x: a.x + this.x, y: a.y + this.y, width: a.width, height: a.height});
    return a
}, destroy: function () {
    AmCharts.remove(this.set);
    AmCharts.remove(this.labelsSet);
    var a = this.axisLine;
    a && AmCharts.remove(a.set);
    AmCharts.remove(this.grid0)
}});
AmCharts.ValueAxis = AmCharts.Class({inherits: AmCharts.AxisBase, construct: function (a) {
    this.cname = "ValueAxis";
    this.createEvents("axisChanged", "logarithmicAxisFailed", "axisSelfZoomed", "axisZoomed");
    AmCharts.ValueAxis.base.construct.call(this, a);
    this.dataChanged = !0;
    this.stackType = "none";
    this.position = "left";
    this.unitPosition = "right";
    this.recalculateToPercents = this.includeHidden = this.includeGuidesInMinMax = this.integersOnly = !1;
    this.durationUnits = {DD: "d. ", hh: ":", mm: ":", ss: ""};
    this.scrollbar = !1;
    this.baseValue =
        0;
    this.radarCategoriesEnabled = !0;
    this.gridType = "polygons";
    this.useScientificNotation = !1;
    this.axisTitleOffset = 10;
    this.minMaxMultiplier = 1;
    this.logGridLimit = 2;
    AmCharts.applyTheme(this, a, this.cname)
}, updateData: function () {
    0 >= this.gridCountR && (this.gridCountR = 1);
    this.totals = [];
    this.data = this.chart.chartData;
    var a = this.chart;
    "xy" != a.type && (this.stackGraphs("smoothedLine"), this.stackGraphs("line"), this.stackGraphs("column"), this.stackGraphs("step"));
    this.recalculateToPercents && this.recalculate();
    this.synchronizationMultiplier &&
        this.synchronizeWith ? (AmCharts.isString(this.synchronizeWith) && (this.synchronizeWith = a.getValueAxisById(this.synchronizeWith)), this.synchronizeWith && (this.synchronizeWithAxis(this.synchronizeWith), this.foundGraphs = !0)) : (this.foundGraphs = !1, this.getMinMax())
}, draw: function () {
    AmCharts.ValueAxis.base.draw.call(this);
    var a = this.chart, b = this.set;
    "duration" == this.type && (this.duration = "ss");
    !0 === this.dataChanged && (this.updateData(), this.dataChanged = !1);
    if (this.logarithmic && (0 >= this.getMin(0, this.data.length -
        1) || 0 >= this.minimum))this.fire("logarithmicAxisFailed", {type: "logarithmicAxisFailed", chart: a}); else {
        this.grid0 = null;
        var c, d, f = a.dx, e = a.dy, g = !1, h = this.logarithmic;
        if (isNaN(this.min) || isNaN(this.max) || !this.foundGraphs || Infinity == this.min || -Infinity == this.max)g = !0; else {
            var k = this.labelFrequency, l = this.showFirstLabel, m = this.showLastLabel, p = 1, n = 0, q = Math.round((this.max - this.min) / this.step) + 1, s;
            !0 === h ? (s = Math.log(this.max) * Math.LOG10E - Math.log(this.minReal) * Math.LOG10E, this.stepWidth = this.axisWidth / s,
                s > this.logGridLimit && (q = Math.ceil(Math.log(this.max) * Math.LOG10E) + 1, n = Math.round(Math.log(this.minReal) * Math.LOG10E), q > this.gridCountR && (p = Math.ceil(q / this.gridCountR)))) : this.stepWidth = this.axisWidth / (this.max - this.min);
            var r = 0;
            1 > this.step && -1 < this.step && (r = AmCharts.getDecimals(this.step));
            this.integersOnly && (r = 0);
            r > this.maxDecCount && (r = this.maxDecCount);
            var u = this.precision;
            isNaN(u) || (r = u);
            this.max = AmCharts.roundTo(this.max, this.maxDecCount);
            this.min = AmCharts.roundTo(this.min, this.maxDecCount);
            var v = {};
            v.precision = r;
            v.decimalSeparator = a.numberFormatter.decimalSeparator;
            v.thousandsSeparator = a.numberFormatter.thousandsSeparator;
            this.numberFormatter = v;
            var t, w = this.guides, z = w.length;
            if (0 < z) {
                c = this.fillAlpha;
                for (d = this.fillAlpha = 0; d < z; d++) {
                    var F = w[d], y = NaN, B = F.above;
                    isNaN(F.toValue) || (y = this.getCoordinate(F.toValue), t = new this.axisItemRenderer(this, y, "", !0, NaN, NaN, F), this.pushAxisItem(t, B));
                    var G = NaN;
                    isNaN(F.value) || (G = this.getCoordinate(F.value), t = new this.axisItemRenderer(this, G, F.label, !0,
                        NaN, (y - G) / 2, F), this.pushAxisItem(t, B));
                    isNaN(y - G) || (t = new this.guideFillRenderer(this, G, y, F), this.pushAxisItem(t, B), t = t.graphics(), F.graphics = t, F.balloonText && this.addEventListeners(t, F))
                }
                this.fillAlpha = c
            }
            w = !1;
            for (d = n; d < q; d += p)z = AmCharts.roundTo(this.step * d + this.min, r), -1 != String(z).indexOf("e") && (w = !0, String(z).split("e"));
            this.duration && (this.maxInterval = AmCharts.getMaxInterval(this.max, this.duration));
            var r = this.step, K, z = this.minorGridAlpha;
            this.minorGridEnabled && (K = this.getMinorGridStep(r, this.stepWidth *
                r));
            for (d = n; d < q; d += p)if (n = r * d + this.min, n = AmCharts.roundTo(n, this.maxDecCount + 1), !this.integersOnly || Math.round(n) == n)if (isNaN(u) || Number(AmCharts.toFixed(n, u)) == n) {
                !0 === h && (0 === n && (n = this.minReal), s > this.logGridLimit && (n = Math.pow(10, d)), w = -1 != String(n).indexOf("e") ? !0 : !1);
                this.useScientificNotation && (w = !0);
                this.usePrefixes && (w = !1);
                w ? (t = -1 == String(n).indexOf("e") ? n.toExponential(15) : String(n), c = t.split("e"), t = Number(c[0]), c = Number(c[1]), t = AmCharts.roundTo(t, 14), 10 == t && (t = 1, c += 1), t = t + "e" + c, 0 === n && (t =
                    "0"), 1 == n && (t = "1")) : (h && (t = String(n).split("."), t[1] ? (v.precision = t[1].length, 0 > d && (v.precision = Math.abs(d))) : v.precision = -1), t = this.usePrefixes ? AmCharts.addPrefix(n, a.prefixesOfBigNumbers, a.prefixesOfSmallNumbers, v, !0) : AmCharts.formatNumber(n, v, v.precision));
                this.duration && (t = AmCharts.formatDuration(n, this.duration, "", this.durationUnits, this.maxInterval, v));
                this.recalculateToPercents ? t += "%" : (c = this.unit) && (t = "left" == this.unitPosition ? c + t : t + c);
                Math.round(d / k) != d / k && (t = void 0);
                if (0 === d && !l || d == q - 1 && !m)t = " ";
                c = this.getCoordinate(n);
                this.labelFunction && (t = this.labelFunction(n, t, this).toString());
                t = new this.axisItemRenderer(this, c, t);
                this.pushAxisItem(t);
                if (n == this.baseValue && "radar" != a.type) {
                    var A, S, B = this.viW, y = this.viH;
                    t = this.viX;
                    F = this.viY;
                    "H" == this.orientation ? 0 <= c && c <= B + 1 && (A = [c, c, c + f], S = [y, 0, e]) : 0 <= c && c <= y + 1 && (A = [0, B, B + f], S = [c, c, c + e]);
                    A && (c = AmCharts.fitToBounds(2 * this.gridAlpha, 0, 1), c = AmCharts.line(a.container, A, S, this.gridColor, c, 1, this.dashLength), c.translate(t, F), this.grid0 = c, a.axesSet.push(c),
                        c.toBack())
                }
                if (!isNaN(K) && 0 < z && d < q - 1) {
                    t = this.gridAlpha;
                    this.gridAlpha = this.minorGridAlpha;
                    for (c = 1; c < r / K; c++)F = this.getCoordinate(n + K * c), F = new this.axisItemRenderer(this, F, "", !1, 0, 0, !1, !1, 0, !0), this.pushAxisItem(F);
                    this.gridAlpha = t
                }
            }
            d = this.baseValue;
            this.min > this.baseValue && this.max > this.baseValue && (d = this.min);
            this.min < this.baseValue && this.max < this.baseValue && (d = this.max);
            h && d < this.minReal && (d = this.minReal);
            this.baseCoord = this.getCoordinate(d);
            d = {type: "axisChanged", target: this, chart: a};
            d.min = h ? this.minReal :
                this.min;
            d.max = this.max;
            this.fire("axisChanged", d);
            this.axisCreated = !0
        }
        h = this.axisLine.set;
        d = this.labelsSet;
        this.positionTitle();
        "radar" != a.type ? (a = this.viX, f = this.viY, b.translate(a, f), d.translate(a, f)) : h.toFront();
        !this.visible || g ? (b.hide(), h.hide(), d.hide()) : (b.show(), h.show(), d.show());
        this.axisY = this.y - this.viY;
        this.axisX = this.x - this.viX
    }
}, getMinorGridStep: function (a, b) {
    var c = [5, 4, 2];
    60 > b && c.shift();
    for (var d = Math.floor(Math.log(Math.abs(a)) * Math.LOG10E), f = 0; f < c.length; f++) {
        var e = a / c[f], g = Math.floor(Math.log(Math.abs(e)) *
            Math.LOG10E);
        if (!(0 < Math.abs(d - g)))if (1 > a) {
            if (g = Math.pow(10, -g) * e, g == Math.round(g))return e
        } else if (e == Math.round(e))return e
    }
}, stackGraphs: function (a) {
    var b = this.stackType;
    "stacked" == b && (b = "regular");
    "line" == b && (b = "none");
    "100% stacked" == b && (b = "100%");
    this.stackType = b;
    var c = [], d = [], f = [], e = [], g, h = this.chart.graphs, k, l, m, p, n = this.baseValue, q = !1;
    if ("line" == a || "step" == a || "smoothedLine" == a)q = !0;
    if (q && ("regular" == b || "100%" == b))for (p = 0; p < h.length; p++)m = h[p], m.hidden || (l = m.type, m.chart == this.chart && m.valueAxis ==
        this && a == l && m.stackable && (k && (m.stackGraph = k), k = m));
    for (k = this.start; k <= this.end; k++) {
        var s = 0;
        for (p = 0; p < h.length; p++)if (m = h[p], !m.hidden && (l = m.type, m.chart == this.chart && m.valueAxis == this && a == l && m.stackable && (l = this.data[k].axes[this.id].graphs[m.id], g = l.values.value, !isNaN(g)))) {
            var r = AmCharts.getDecimals(g);
            s < r && (s = r);
            isNaN(e[k]) ? e[k] = Math.abs(g) : e[k] += Math.abs(g);
            e[k] = AmCharts.roundTo(e[k], s);
            m = m.fillToGraph;
            q && m && (m = this.data[k].axes[this.id].graphs[m.id]) && (l.values.open = m.values.value);
            "regular" ==
                b && (q && (isNaN(c[k]) ? (c[k] = g, l.values.close = g, l.values.open = this.baseValue) : (isNaN(g) ? l.values.close = c[k] : l.values.close = g + c[k], l.values.open = c[k], c[k] = l.values.close)), "column" != a || isNaN(g) || (l.values.close = g, 0 > g ? (l.values.close = g, isNaN(d[k]) ? l.values.open = n : (l.values.close += d[k], l.values.open = d[k]), d[k] = l.values.close) : (l.values.close = g, isNaN(f[k]) ? l.values.open = n : (l.values.close += f[k], l.values.open = f[k]), f[k] = l.values.close)))
        }
    }
    for (k = this.start; k <= this.end; k++)for (p = 0; p < h.length; p++)m = h[p], m.hidden ||
        (l = m.type, m.chart == this.chart && m.valueAxis == this && a == l && m.stackable && (l = this.data[k].axes[this.id].graphs[m.id], g = l.values.value, isNaN(g) || (c = g / e[k] * 100, l.values.percents = c, l.values.total = e[k], "100%" == b && (isNaN(d[k]) && (d[k] = 0), isNaN(f[k]) && (f[k] = 0), 0 > c ? (l.values.close = AmCharts.fitToBounds(c + d[k], -100, 100), l.values.open = d[k], d[k] = l.values.close) : (l.values.close = AmCharts.fitToBounds(c + f[k], -100, 100), l.values.open = f[k], f[k] = l.values.close)))))
}, recalculate: function () {
    var a = this.chart.graphs, b;
    for (b =
             0; b < a.length; b++) {
        var c = a[b];
        if (c.valueAxis == this) {
            var d = "value";
            if ("candlestick" == c.type || "ohlc" == c.type)d = "open";
            var f, e, g = this.end + 2, g = AmCharts.fitToBounds(this.end + 1, 0, this.data.length - 1), h = this.start;
            0 < h && h--;
            var k;
            e = this.start;
            c.compareFromStart && (e = 0);
            for (k = e; k <= g && (e = this.data[k].axes[this.id].graphs[c.id], f = e.values[d], isNaN(f)); k++);
            for (d = h; d <= g; d++) {
                e = this.data[d].axes[this.id].graphs[c.id];
                e.percents = {};
                var h = e.values, l;
                for (l in h)e.percents[l] = "percents" != l ? h[l] / f * 100 - 100 : h[l]
            }
        }
    }
}, getMinMax: function () {
    var a =
        !1, b = this.chart, c = b.graphs, d;
    for (d = 0; d < c.length; d++) {
        var f = c[d].type;
        ("line" == f || "step" == f || "smoothedLine" == f) && this.expandMinMax && (a = !0)
    }
    a && (0 < this.start && this.start--, this.end < this.data.length - 1 && this.end++);
    "serial" == b.type && (!0 !== b.categoryAxis.parseDates || a || this.end < this.data.length - 1 && this.end++);
    a = this.minMaxMultiplier;
    this.min = this.getMin(this.start, this.end);
    this.max = this.getMax();
    a = (this.max - this.min) * (a - 1);
    this.min -= a;
    this.max += a;
    a = this.guides.length;
    if (this.includeGuidesInMinMax && 0 < a)for (b =
                                                     0; b < a; b++)c = this.guides[b], c.toValue < this.min && (this.min = c.toValue), c.value < this.min && (this.min = c.value), c.toValue > this.max && (this.max = c.toValue), c.value > this.max && (this.max = c.value);
    isNaN(this.minimum) || (this.min = this.minimum);
    isNaN(this.maximum) || (this.max = this.maximum);
    this.min > this.max && (a = this.max, this.max = this.min, this.min = a);
    isNaN(this.minTemp) || (this.min = this.minTemp);
    isNaN(this.maxTemp) || (this.max = this.maxTemp);
    this.minReal = this.min;
    this.maxReal = this.max;
    0 === this.min && 0 === this.max && (this.max =
        9);
    this.min > this.max && (this.min = this.max - 1);
    a = this.min;
    b = this.max;
    c = this.max - this.min;
    d = 0 === c ? Math.pow(10, Math.floor(Math.log(Math.abs(this.max)) * Math.LOG10E)) / 10 : Math.pow(10, Math.floor(Math.log(Math.abs(c)) * Math.LOG10E)) / 10;
    isNaN(this.maximum) && isNaN(this.maxTemp) && (this.max = Math.ceil(this.max / d) * d + d);
    isNaN(this.minimum) && isNaN(this.minTemp) && (this.min = Math.floor(this.min / d) * d - d);
    0 > this.min && 0 <= a && (this.min = 0);
    0 < this.max && 0 >= b && (this.max = 0);
    "100%" == this.stackType && (this.min = 0 > this.min ? -100 : 0, this.max =
        0 > this.max ? 0 : 100);
    c = this.max - this.min;
    d = Math.pow(10, Math.floor(Math.log(Math.abs(c)) * Math.LOG10E)) / 10;
    this.step = Math.ceil(c / this.gridCountR / d) * d;
    c = Math.pow(10, Math.floor(Math.log(Math.abs(this.step)) * Math.LOG10E));
    c = this.fixStepE(c);
    d = Math.ceil(this.step / c);
    5 < d && (d = 10);
    5 >= d && 2 < d && (d = 5);
    this.step = Math.ceil(this.step / (c * d)) * c * d;
    1 > c ? (this.maxDecCount = Math.abs(Math.log(Math.abs(c)) * Math.LOG10E), this.maxDecCount = Math.round(this.maxDecCount), this.step = AmCharts.roundTo(this.step, this.maxDecCount + 1)) : this.maxDecCount =
        0;
    this.min = this.step * Math.floor(this.min / this.step);
    this.max = this.step * Math.ceil(this.max / this.step);
    0 > this.min && 0 <= a && (this.min = 0);
    0 < this.max && 0 >= b && (this.max = 0);
    1 < this.minReal && 1 < this.max - this.minReal && (this.minReal = Math.floor(this.minReal));
    c = Math.pow(10, Math.floor(Math.log(Math.abs(this.minReal)) * Math.LOG10E));
    0 === this.min && (this.minReal = c);
    0 === this.min && 1 < this.minReal && (this.minReal = 1);
    0 < this.min && 0 < this.minReal - this.step && (this.minReal = this.min + this.step < this.minReal ? this.min + this.step : this.min);
    c = Math.log(b) * Math.LOG10E - Math.log(a) * Math.LOG10E;
    this.logarithmic && (2 < c ? (this.minReal = this.min = Math.pow(10, Math.floor(Math.log(Math.abs(a)) * Math.LOG10E)), this.max = Math.pow(10, Math.ceil(Math.log(Math.abs(b)) * Math.LOG10E))) : (b = Math.pow(10, Math.floor(Math.log(Math.abs(this.min)) * Math.LOG10E)) / 10, a = Math.pow(10, Math.floor(Math.log(Math.abs(a)) * Math.LOG10E)) / 10, b < a && (this.minReal = this.min = 10 * a)))
}, fixStepE: function (a) {
    a = a.toExponential(0).split("e");
    var b = Number(a[1]);
    9 == Number(a[0]) && b++;
    return this.generateNumber(1,
        b)
}, generateNumber: function (a, b) {
    var c = "", d;
    d = 0 > b ? Math.abs(b) - 1 : Math.abs(b);
    var f;
    for (f = 0; f < d; f++)c += "0";
    return 0 > b ? Number("0." + c + String(a)) : Number(String(a) + c)
}, getMin: function (a, b) {
    var c, d;
    for (d = a; d <= b; d++) {
        var f = this.data[d].axes[this.id].graphs, e;
        for (e in f)if (f.hasOwnProperty(e)) {
            var g = this.chart.getGraphById(e);
            if (g.includeInMinMax && (!g.hidden || this.includeHidden)) {
                isNaN(c) && (c = Infinity);
                this.foundGraphs = !0;
                g = f[e].values;
                this.recalculateToPercents && (g = f[e].percents);
                var h;
                if (this.minMaxField)h =
                    g[this.minMaxField], h < c && (c = h); else for (var k in g)g.hasOwnProperty(k) && "percents" != k && "total" != k && (h = g[k], h < c && (c = h))
            }
        }
    }
    return c
}, getMax: function () {
    var a, b;
    for (b = this.start; b <= this.end; b++) {
        var c = this.data[b].axes[this.id].graphs, d;
        for (d in c)if (c.hasOwnProperty(d)) {
            var f = this.chart.getGraphById(d);
            if (f.includeInMinMax && (!f.hidden || this.includeHidden)) {
                isNaN(a) && (a = -Infinity);
                this.foundGraphs = !0;
                f = c[d].values;
                this.recalculateToPercents && (f = c[d].percents);
                var e;
                if (this.minMaxField)e = f[this.minMaxField],
                    e > a && (a = e); else for (var g in f)f.hasOwnProperty(g) && "percents" != g && "total" != g && (e = f[g], e > a && (a = e))
            }
        }
    }
    return a
}, dispatchZoomEvent: function (a, b) {
    var c = {type: "axisZoomed", startValue: a, endValue: b, target: this, chart: this.chart};
    this.fire(c.type, c)
}, zoomToValues: function (a, b) {
    if (b < a) {
        var c = b;
        b = a;
        a = c
    }
    a < this.min && (a = this.min);
    b > this.max && (b = this.max);
    c = {type: "axisSelfZoomed"};
    c.chart = this.chart;
    c.valueAxis = this;
    c.multiplier = this.axisWidth / Math.abs(this.getCoordinate(b) - this.getCoordinate(a));
    c.position = "V" ==
        this.orientation ? this.reversed ? this.getCoordinate(a) : this.getCoordinate(b) : this.reversed ? this.getCoordinate(b) : this.getCoordinate(a);
    this.fire(c.type, c)
}, coordinateToValue: function (a) {
    if (isNaN(a))return NaN;
    var b = this.axisWidth, c = this.stepWidth, d = this.reversed, f = this.rotate, e = this.min, g = this.minReal;
    return!0 === this.logarithmic ? Math.pow(10, (f ? !0 === d ? (b - a) / c : a / c : !0 === d ? a / c : (b - a) / c) + Math.log(g) * Math.LOG10E) : !0 === d ? f ? e - (a - b) / c : a / c + e : f ? a / c + e : e - (a - b) / c
}, getCoordinate: function (a) {
    if (isNaN(a))return NaN;
    var b = this.rotate, c = this.reversed, d = this.axisWidth, f = this.stepWidth, e = this.min, g = this.minReal;
    !0 === this.logarithmic ? (a = Math.log(a) * Math.LOG10E - Math.log(g) * Math.LOG10E, b = b ? !0 === c ? d - f * a : f * a : !0 === c ? f * a : d - f * a) : b = !0 === c ? b ? d - f * (a - e) : f * (a - e) : b ? f * (a - e) : d - f * (a - e);
    b = this.rotate ? b + (this.x - this.viX) : b + (this.y - this.viY);
    return Math.round(b)
}, synchronizeWithAxis: function (a) {
    this.synchronizeWith = a;
    this.listenTo(this.synchronizeWith, "axisChanged", this.handleSynchronization)
}, handleSynchronization: function (a) {
    var b =
        this.synchronizeWith;
    a = b.min;
    var c = b.max, b = b.step, d = this.synchronizationMultiplier;
    d && (this.min = a * d, this.max = c * d, this.step = b * d, a = Math.pow(10, Math.floor(Math.log(Math.abs(this.step)) * Math.LOG10E)), a = Math.abs(Math.log(Math.abs(a)) * Math.LOG10E), this.maxDecCount = a = Math.round(a), this.draw())
}});
AmCharts.RecAxis = AmCharts.Class({construct: function (a) {
    var b = a.chart, c = a.axisThickness, d = a.axisColor, f = a.axisAlpha, e = a.offset, g = a.dx, h = a.dy, k = a.viX, l = a.viY, m = a.viH, p = a.viW, n = b.container;
    "H" == a.orientation ? (d = AmCharts.line(n, [0, p], [0, 0], d, f, c), this.axisWidth = a.width, "bottom" == a.position ? (a = c / 2 + e + m + l - 1, c = k) : (a = -c / 2 - e + l + h, c = g + k)) : (this.axisWidth = a.height, "right" == a.position ? (d = AmCharts.line(n, [0, 0, -g], [0, m, m - h], d, f, c), a = l + h, c = c / 2 + e + g + p + k - 1) : (d = AmCharts.line(n, [0, 0], [0, m], d, f, c), a = l, c = -c / 2 - e + k));
    d.translate(c,
        a);
    b.axesSet.push(d);
    this.set = d
}});
AmCharts.RecItem = AmCharts.Class({construct: function (a, b, c, d, f, e, g, h, k, l) {
    b = Math.round(b);
    void 0 == c && (c = "");
    k || (k = 0);
    void 0 == d && (d = !0);
    var m = a.chart.fontFamily, p = a.fontSize;
    void 0 == p && (p = a.chart.fontSize);
    var n = a.color;
    void 0 == n && (n = a.chart.color);
    var q = a.chart.container, s = q.set();
    this.set = s;
    var r = a.axisThickness, u = a.axisColor, v = a.axisAlpha, t = a.tickLength, w = a.gridAlpha, z = a.gridThickness, F = a.gridColor, y = a.dashLength, B = a.fillColor, G = a.fillAlpha, K = a.labelsEnabled, A = a.labelRotation, S = a.counter, T = a.inside,
        ca = a.dx, U = a.dy, Na = a.orientation, ga = a.position, ma = a.previousCoord, Q = a.viH, V = a.viW, $ = a.offset, ra, N;
    g ? (K = !0, isNaN(g.tickLength) || (t = g.tickLength), void 0 != g.lineColor && (F = g.lineColor), void 0 != g.color && (n = g.color), isNaN(g.lineAlpha) || (w = g.lineAlpha), isNaN(g.dashLength) || (y = g.dashLength), isNaN(g.lineThickness) || (z = g.lineThickness), !0 === g.inside && (T = !0), isNaN(g.labelRotation) || (A = g.labelRotation), isNaN(g.fontSize) || (p = g.fontSize), g.position && (ga = g.position)) : "" === c && (t = 0);
    N = "start";
    f && (N = "middle");
    var W =
        A * Math.PI / 180, pa, H = 0, E = 0, R = 0, da = pa = 0, ha = 0;
    "V" == Na && (A = 0);
    var x;
    K && (x = a.autoWrap && 0 === A ? AmCharts.wrappedText(q, c, n, m, p, N, h, f, 0) : AmCharts.text(q, c, n, m, p, N, h), N = x.getBBox(), da = N.width, ha = N.height);
    if ("H" == Na) {
        if (0 <= b && b <= V + 1 && (0 < t && 0 < v && b + k <= V + 1 && (ra = AmCharts.line(q, [b + k, b + k], [0, t], u, v, z), s.push(ra)), 0 < w && (N = AmCharts.line(q, [b, b + ca, b + ca], [Q, Q + U, U], F, w, z, y), s.push(N))), E = 0, H = b, g && 90 == A && (H -= p), !1 === d ? (N = "start", E = "bottom" == ga ? T ? E + t : E - t : T ? E - t : E + t, H += 3, f && (H += f / 2, N = "middle"), 0 < A && (N = "middle")) : N = "middle",
            1 == S && 0 < G && !g && !l && ma < V && (d = AmCharts.fitToBounds(b, 0, V), ma = AmCharts.fitToBounds(ma, 0, V), pa = d - ma, 0 < pa && (fill = AmCharts.rect(q, pa, a.height, B, G), fill.translate(d - pa + ca, U), s.push(fill))), "bottom" == ga ? (E += Q + p / 2 + $, T ? 0 < A ? (E = Q - da / 2 * Math.sin(W) - t - 3, H += da / 2 * Math.cos(W) - 4 + 2) : 0 > A ? (E = Q + da * Math.sin(W) - t - 3 + 2, H += -da * Math.cos(W) - ha * Math.sin(W) - 4) : E -= t + p + 3 + 3 : 0 < A ? (E = Q + da / 2 * Math.sin(W) + t + 3, H -= da / 2 * Math.cos(W)) : 0 > A ? (E = Q + t + 3 - da / 2 * Math.sin(W) + 2, H += da / 2 * Math.cos(W)) : E += t + r + 3 + 3) : (E += U + p / 2 - $, H += ca, T ? 0 < A ? (E = da / 2 * Math.sin(W) +
            t + 3, H -= da / 2 * Math.cos(W)) : E += t + 3 : 0 < A ? (E = -(da / 2) * Math.sin(W) - t - 6, H += da / 2 * Math.cos(W)) : E -= t + p + 3 + r + 3), "bottom" == ga ? pa = (T ? Q - t - 1 : Q + r - 1) + $ : (R = ca, pa = (T ? U : U - t - r + 1) - $), e && (H += e), U = H, 0 < A && (U += da / 2 * Math.cos(W)), x && (ga = 0, T && (ga = da / 2 * Math.cos(W)), U + ga > V + 2 || 0 > U))x.remove(), x = null
    } else {
        0 <= b && b <= Q + 1 && (0 < t && 0 < v && b + k <= Q + 1 && (ra = AmCharts.line(q, [0, t], [b + k, b + k], u, v, z), s.push(ra)), 0 < w && (N = AmCharts.line(q, [0, ca, V + ca], [b, b + U, b + U], F, w, z, y), s.push(N)));
        N = "end";
        if (!0 === T && "left" == ga || !1 === T && "right" == ga)N = "start";
        E = b - p / 2;
        1 ==
            S && 0 < G && !g && !l && (d = AmCharts.fitToBounds(b, 0, Q), ma = AmCharts.fitToBounds(ma, 0, Q), W = d - ma, fill = AmCharts.polygon(q, [0, a.width, a.width, 0], [0, 0, W, W], B, G), fill.translate(ca, d - W + U), s.push(fill));
        E += p / 2;
        "right" == ga ? (H += ca + V + $, E += U, T ? (H -= t + 4, e || (E -= p / 2 + 3)) : (H += t + 4 + r, E -= 2)) : T ? (H += t + 4 - $, e || (E -= p / 2 + 3), g && (H += ca, E += U)) : (H += -t - r - 4 - 2 - $, E -= 2);
        ra && ("right" == ga ? (R += ca + $ + V, pa += U, R = T ? R - r : R + r) : (R -= $, T || (R -= t + r)));
        e && (E += e);
        T = -3;
        "right" == ga && (T += U);
        x && (E > Q + 1 || E < T) && (x.remove(), x = null)
    }
    ra && ra.translate(R, pa);
    !1 === a.visible &&
    (ra && ra.remove(), x && (x.remove(), x = null));
    x && (x.attr({"text-anchor": N}), x.translate(H, E), 0 !== A && x.rotate(-A, a.chart.backgroundColor), a.allLabels.push(x), " " != c && (this.label = x));
    l || (a.counter = 0 === S ? 1 : 0, a.previousCoord = b);
    0 === this.set.node.childNodes.length && this.set.remove()
}, graphics: function () {
    return this.set
}, getLabel: function () {
    return this.label
}});
AmCharts.RecFill = AmCharts.Class({construct: function (a, b, c, d) {
    var f = a.dx, e = a.dy, g = a.orientation, h = 0;
    if (c < b) {
        var k = b;
        b = c;
        c = k
    }
    var l = d.fillAlpha;
    isNaN(l) && (l = 0);
    k = a.chart.container;
    d = d.fillColor;
    "V" == g ? (b = AmCharts.fitToBounds(b, 0, a.viH), c = AmCharts.fitToBounds(c, 0, a.viH)) : (b = AmCharts.fitToBounds(b, 0, a.viW), c = AmCharts.fitToBounds(c, 0, a.viW));
    c -= b;
    isNaN(c) && (c = 4, h = 2, l = 0);
    0 > c && "object" == typeof d && (d = d.join(",").split(",").reverse());
    "V" == g ? (a = AmCharts.rect(k, a.width, c, d, l), a.translate(f, b - h + e)) : (a = AmCharts.rect(k,
        c, a.height, d, l), a.translate(b - h + f, e));
    this.set = k.set([a])
}, graphics: function () {
    return this.set
}, getLabel: function () {
}});
AmCharts.AmChart = AmCharts.Class({construct: function (a) {
    this.theme = a;
    this.version = "3.4.4";
    AmCharts.addChart(this);
    this.createEvents("dataUpdated", "init", "rendered", "drawn");
    this.height = this.width = "100%";
    this.dataChanged = !0;
    this.chartCreated = !1;
    this.previousWidth = this.previousHeight = 0;
    this.backgroundColor = "#FFFFFF";
    this.borderAlpha = this.backgroundAlpha = 0;
    this.color = this.borderColor = "#000000";
    this.fontFamily = "Verdana";
    this.fontSize = 11;
    this.usePrefixes = !1;
    this.numberFormatter = {precision: -1, decimalSeparator: ".",
        thousandsSeparator: ","};
    this.percentFormatter = {precision: 2, decimalSeparator: ".", thousandsSeparator: ","};
    this.labels = [];
    this.allLabels = [];
    this.titles = [];
    this.marginRight = this.marginLeft = this.autoMarginOffset = 0;
    this.timeOuts = [];
    this.creditsPosition = "top-left";
    var b = document.createElement("div"), c = b.style;
    c.overflow = "hidden";
    c.position = "relative";
    c.textAlign = "left";
    this.chartDiv = b;
    b = document.createElement("div");
    c = b.style;
    c.overflow = "hidden";
    c.position = "relative";
    c.textAlign = "left";
    this.legendDiv = b;
    this.titleHeight = 0;
    this.hideBalloonTime = 150;
    this.handDrawScatter = 2;
    this.handDrawThickness = 1;
    this.prefixesOfBigNumbers = [
        {number: 1E3, prefix: "k"},
        {number: 1E6, prefix: "M"},
        {number: 1E9, prefix: "G"},
        {number: 1E12, prefix: "T"},
        {number: 1E15, prefix: "P"},
        {number: 1E18, prefix: "E"},
        {number: 1E21, prefix: "Z"},
        {number: 1E24, prefix: "Y"}
    ];
    this.prefixesOfSmallNumbers = [
        {number: 1E-24, prefix: "y"},
        {number: 1E-21, prefix: "z"},
        {number: 1E-18, prefix: "a"},
        {number: 1E-15, prefix: "f"},
        {number: 1E-12, prefix: "p"},
        {number: 1E-9, prefix: "n"},
        {number: 1E-6, prefix: "\u03bc"},
        {number: 0.001, prefix: "m"}
    ];
    this.panEventsEnabled = !0;
    AmCharts.bezierX = 3;
    AmCharts.bezierY = 6;
    this.product = "amcharts";
    this.animations = [];
    this.balloon = new AmCharts.AmBalloon(this.theme);
    this.balloon.chart = this;
    AmCharts.applyTheme(this, a, "AmChart")
}, drawChart: function () {
    this.drawBackground();
    this.redrawLabels();
    this.drawTitles();
    this.brr()
}, drawBackground: function () {
    AmCharts.remove(this.background);
    var a = this.container, b = this.backgroundColor, c = this.backgroundAlpha, d = this.set;
    AmCharts.isModern || 0 !== c || (c = 0.001);
    var f = this.updateWidth();
    this.realWidth = f;
    var e = this.updateHeight();
    this.realHeight = e;
    this.background = b = AmCharts.polygon(a, [0, f - 1, f - 1, 0], [0, 0, e - 1, e - 1], b, c, 1, this.borderColor, this.borderAlpha);
    d.push(b);
    if (b = this.backgroundImage)this.path && (b = this.path + b), this.bgImg = a = a.image(b, 0, 0, f, e), d.push(a)
}, drawTitles: function () {
    var a = this.titles;
    if (AmCharts.ifArray(a)) {
        var b = 20, c;
        for (c = 0; c < a.length; c++) {
            var d = a[c], f = d.color;
            void 0 === f && (f = this.color);
            var e = d.size;
            isNaN(d.alpha);
            var g = this.marginLeft, f = AmCharts.text(this.container, d.text, f, this.fontFamily, e);
            f.translate(g + (this.realWidth - this.marginRight - g) / 2, b);
            g = !0;
            void 0 !== d.bold && (g = d.bold);
            g && f.attr({"font-weight": "bold"});
            f.attr({opacity: d.alpha});
            b += e + 6;
            this.freeLabelsSet.push(f)
        }
    }
}, write: function (a) {
    a = "object" != typeof a ? document.getElementById(a) : a;
    a.innerHTML = "";
    this.div = a;
    a.style.overflow = "hidden";
    a.style.textAlign = "left";
    var b = this.chartDiv, c = this.legendDiv, d = this.legend, f = c.style, e = b.style;
    this.measure();
    var g,
        h = document.createElement("div");
    g = h.style;
    g.position = "relative";
    this.containerDiv = h;
    a.appendChild(h);
    var k = this.exportConfig;
    k && AmCharts.AmExport && !this.AmExport && (this.AmExport = new AmCharts.AmExport(this, k));
    if (d)switch (d = this.addLegend(d, d.divId), d.position) {
        case "bottom":
            h.appendChild(b);
            h.appendChild(c);
            break;
        case "top":
            h.appendChild(c);
            h.appendChild(b);
            break;
        case "absolute":
            g.width = a.style.width;
            g.height = a.style.height;
            f.position = "absolute";
            e.position = "absolute";
            void 0 !== d.left && (f.left = d.left +
                "px");
            void 0 !== d.right && (f.right = d.right + "px");
            void 0 !== d.top && (f.top = d.top + "px");
            void 0 !== d.bottom && (f.bottom = d.bottom + "px");
            d.marginLeft = 0;
            d.marginRight = 0;
            h.appendChild(b);
            h.appendChild(c);
            break;
        case "right":
            g.width = a.style.width;
            g.height = a.style.height;
            f.position = "relative";
            e.position = "absolute";
            h.appendChild(b);
            h.appendChild(c);
            break;
        case "left":
            g.width = a.style.width;
            g.height = a.style.height;
            f.position = "absolute";
            e.position = "relative";
            h.appendChild(b);
            h.appendChild(c);
            break;
        case "outside":
            h.appendChild(b)
    } else h.appendChild(b);
    this.listenersAdded || (this.addListeners(), this.listenersAdded = !0);
    this.initChart()
}, createLabelsSet: function () {
    AmCharts.remove(this.labelsSet);
    this.labelsSet = this.container.set();
    this.freeLabelsSet.push(this.labelsSet)
}, initChart: function () {
    this.divIsFixed = AmCharts.findIfFixed(this.chartDiv);
    this.previousHeight = this.divRealHeight;
    this.previousWidth = this.divRealWidth;
    this.destroy();
    this.startInterval();
    var a = 0;
    document.attachEvent && !window.opera && (a = 1);
    this.dmouseX = this.dmouseY = 0;
    var b = document.getElementsByTagName("html")[0];
    b && window.getComputedStyle && (b = window.getComputedStyle(b, null)) && (this.dmouseY = AmCharts.removePx(b.getPropertyValue("margin-top")), this.dmouseX = AmCharts.removePx(b.getPropertyValue("margin-left")));
    this.mouseMode = a;
    a = new AmCharts.AmDraw(this.chartDiv, this.realWidth, this.realHeight, this);
    a.handDrawn = this.handDrawn;
    a.handDrawScatter = this.handDrawScatter;
    a.handDrawThickness = this.handDrawThickness;
    this.container = a;
    if (AmCharts.VML || AmCharts.SVG)a = this.container, this.set = a.set(), this.gridSet = a.set(), this.graphsBehindSet =
        a.set(), this.bulletBehindSet = a.set(), this.columnSet = a.set(), this.graphsSet = a.set(), this.trendLinesSet = a.set(), this.axesLabelsSet = a.set(), this.axesSet = a.set(), this.cursorSet = a.set(), this.scrollbarsSet = a.set(), this.bulletSet = a.set(), this.freeLabelsSet = a.set(), this.balloonsSet = a.set(), this.balloonsSet.setAttr("id", "balloons"), this.zoomButtonSet = a.set(), this.linkSet = a.set(), this.renderFix()
}, measure: function () {
    var a = this.div, b = this.chartDiv, c = a.offsetWidth, d = a.offsetHeight, f = this.container;
    a.clientHeight &&
    (c = a.clientWidth, d = a.clientHeight);
    var e = AmCharts.removePx(AmCharts.getStyle(a, "padding-left")), g = AmCharts.removePx(AmCharts.getStyle(a, "padding-right")), h = AmCharts.removePx(AmCharts.getStyle(a, "padding-top")), k = AmCharts.removePx(AmCharts.getStyle(a, "padding-bottom"));
    isNaN(e) || (c -= e);
    isNaN(g) || (c -= g);
    isNaN(h) || (d -= h);
    isNaN(k) || (d -= k);
    e = a.style;
    a = e.width;
    e = e.height;
    -1 != a.indexOf("px") && (c = AmCharts.removePx(a));
    -1 != e.indexOf("px") && (d = AmCharts.removePx(e));
    a = AmCharts.toCoordinate(this.width, c);
    e = AmCharts.toCoordinate(this.height,
        d);
    this.balloon = AmCharts.processObject(this.balloon, AmCharts.AmBalloon, this.theme);
    this.balloon.chart = this;
    if (a != this.previousWidth || e != this.previousHeight)b.style.width = a + "px", b.style.height = e + "px", f && f.setSize(a, e);
    this.balloon.setBounds(2, 2, a - 2, e);
    this.realWidth = a;
    this.realHeight = e;
    this.divRealWidth = c;
    this.divRealHeight = d
}, destroy: function () {
    this.chartDiv.innerHTML = "";
    this.clearTimeOuts();
    this.interval && clearInterval(this.interval);
    this.interval = NaN
}, clearTimeOuts: function () {
    var a = this.timeOuts;
    if (a) {
        var b;
        for (b = 0; b < a.length; b++)clearTimeout(a[b])
    }
    this.timeOuts = []
}, clear: function (a) {
    AmCharts.callMethod("clear", [this.chartScrollbar, this.scrollbarV, this.scrollbarH, this.chartCursor]);
    this.chartCursor = this.scrollbarH = this.scrollbarV = this.chartScrollbar = null;
    this.clearTimeOuts();
    this.container && (this.container.remove(this.chartDiv), this.container.remove(this.legendDiv));
    a || AmCharts.removeChart(this)
}, setMouseCursor: function (a) {
    "auto" == a && AmCharts.isNN && (a = "default");
    this.chartDiv.style.cursor =
        a;
    this.legendDiv.style.cursor = a
}, redrawLabels: function () {
    this.labels = [];
    var a = this.allLabels;
    this.createLabelsSet();
    var b;
    for (b = 0; b < a.length; b++)this.drawLabel(a[b])
}, drawLabel: function (a) {
    if (this.container) {
        var b = a.y, c = a.text, d = a.align, f = a.size, e = a.color, g = a.rotation, h = a.alpha, k = a.bold, l = AmCharts.toCoordinate(a.x, this.realWidth), b = AmCharts.toCoordinate(b, this.realHeight);
        l || (l = 0);
        b || (b = 0);
        void 0 === e && (e = this.color);
        isNaN(f) && (f = this.fontSize);
        d || (d = "start");
        "left" == d && (d = "start");
        "right" == d && (d =
            "end");
        "center" == d && (d = "middle", g ? b = this.realHeight - b + b / 2 : l = this.realWidth / 2 - l);
        void 0 === h && (h = 1);
        void 0 === g && (g = 0);
        b += f / 2;
        c = AmCharts.text(this.container, c, e, this.fontFamily, f, d, k, h);
        c.translate(l, b);
        0 !== g && c.rotate(g);
        a.url && (c.setAttr("cursor", "pointer"), c.click(function () {
            AmCharts.getURL(a.url)
        }));
        this.labelsSet.push(c);
        this.labels.push(c)
    }
}, addLabel: function (a, b, c, d, f, e, g, h, k, l) {
    a = {x: a, y: b, text: c, align: d, size: f, color: e, alpha: h, rotation: g, bold: k, url: l};
    this.container && this.drawLabel(a);
    this.allLabels.push(a)
},
    clearLabels: function () {
        var a = this.labels, b;
        for (b = a.length - 1; 0 <= b; b--)a[b].remove();
        this.labels = [];
        this.allLabels = []
    }, updateHeight: function () {
        var a = this.divRealHeight, b = this.legend;
        if (b) {
            var c = this.legendDiv.offsetHeight, b = b.position;
            if ("top" == b || "bottom" == b) {
                a -= c;
                if (0 > a || isNaN(a))a = 0;
                this.chartDiv.style.height = a + "px"
            }
        }
        return a
    }, updateWidth: function () {
        var a = this.divRealWidth, b = this.divRealHeight, c = this.legend;
        if (c) {
            var d = this.legendDiv, f = d.offsetWidth;
            isNaN(c.width) || (f = c.width);
            var e = d.offsetHeight,
                d = d.style, g = this.chartDiv.style, c = c.position;
            if ("right" == c || "left" == c) {
                a -= f;
                if (0 > a || isNaN(a))a = 0;
                g.width = a + "px";
                "left" == c ? g.left = f + "px" : d.left = a + "px";
                d.top = (b - e) / 2 + "px"
            }
        }
        return a
    }, getTitleHeight: function () {
        var a = 0, b = this.titles;
        if (0 < b.length) {
            var a = 15, c;
            for (c = 0; c < b.length; c++)a += b[c].size + 6
        }
        return a
    }, addTitle: function (a, b, c, d, f) {
        isNaN(b) && (b = this.fontSize + 2);
        a = {text: a, size: b, color: c, alpha: d, bold: f};
        this.titles.push(a);
        return a
    }, addMouseWheel: function () {
        var a = this;
        window.addEventListener && (window.addEventListener("DOMMouseScroll",
            function (b) {
                a.handleWheel.call(a, b)
            }, !1), document.addEventListener("mousewheel", function (b) {
            a.handleWheel.call(a, b)
        }, !1))
    }, handleWheel: function (a) {
        if (this.mouseIsOver) {
            var b = 0;
            a || (a = window.event);
            a.wheelDelta ? b = a.wheelDelta / 120 : a.detail && (b = -a.detail / 3);
            b && this.handleWheelReal(b, a.shiftKey);
            a.preventDefault && a.preventDefault()
        }
    }, handleWheelReal: function (a) {
    }, addListeners: function () {
        var a = this, b = a.chartDiv;
        document.addEventListener ? (a.panEventsEnabled && "ontouchstart"in document.documentElement && (b.addEventListener("touchstart",
            function (b) {
                a.handleTouchMove.call(a, b);
                a.handleTouchStart.call(a, b)
            }, !0), b.addEventListener("touchmove", function (b) {
            a.handleTouchMove.call(a, b)
        }, !0), b.addEventListener("touchend", function (b) {
            a.handleTouchEnd.call(a, b)
        }, !0)), b.addEventListener("mousedown", function (b) {
            a.handleMouseDown.call(a, b)
        }, !0), b.addEventListener("mouseover", function (b) {
            a.handleMouseOver.call(a, b)
        }, !0), b.addEventListener("mouseout", function (b) {
            a.handleMouseOut.call(a, b)
        }, !0)) : (b.attachEvent("onmousedown", function (b) {
            a.handleMouseDown.call(a,
                b)
        }), b.attachEvent("onmouseover", function (b) {
            a.handleMouseOver.call(a, b)
        }), b.attachEvent("onmouseout", function (b) {
            a.handleMouseOut.call(a, b)
        }))
    }, dispDUpd: function () {
        var a;
        this.dispatchDataUpdated && (this.dispatchDataUpdated = !1, a = "dataUpdated", this.fire(a, {type: a, chart: this}));
        this.chartCreated || (a = "init", this.fire(a, {type: a, chart: this}));
        this.chartRendered || (a = "rendered", this.fire(a, {type: a, chart: this}), this.chartRendered = !0);
        a = "drawn";
        this.fire(a, {type: a, chart: this})
    }, validateSize: function () {
        var a =
            this;
        a.measure();
        var b = a.legend;
        if ((a.realWidth != a.previousWidth || a.realHeight != a.previousHeight) && 0 < a.realWidth && 0 < a.realHeight) {
            a.sizeChanged = !0;
            if (b) {
                clearTimeout(a.legendInitTO);
                var c = setTimeout(function () {
                    b.invalidateSize()
                }, 100);
                a.timeOuts.push(c);
                a.legendInitTO = c
            }
            a.marginsUpdated = "xy" != a.type ? !1 : !0;
            clearTimeout(a.initTO);
            c = setTimeout(function () {
                a.initChart()
            }, 150);
            a.timeOuts.push(c);
            a.initTO = c
        }
        a.renderFix();
        b && b.renderFix()
    }, invalidateSize: function () {
        this.previousHeight = this.previousWidth =
            NaN;
        this.invalidateSizeReal()
    }, invalidateSizeReal: function () {
        var a = this;
        a.marginsUpdated = !1;
        clearTimeout(a.validateTO);
        var b = setTimeout(function () {
            a.validateSize()
        }, 5);
        a.timeOuts.push(b);
        a.validateTO = b
    }, validateData: function (a) {
        this.chartCreated && (this.dataChanged = !0, this.marginsUpdated = "xy" != this.type ? !1 : !0, this.initChart(a))
    }, validateNow: function () {
        this.chartRendered = this.listenersAdded = !1;
        this.write(this.div)
    }, showItem: function (a) {
        a.hidden = !1;
        this.initChart()
    }, hideItem: function (a) {
        a.hidden = !0;
        this.initChart()
    }, hideBalloon: function () {
        var a = this;
        clearInterval(a.hoverInt);
        clearTimeout(a.balloonTO);
        a.hoverInt = setTimeout(function () {
            a.hideBalloonReal.call(a)
        }, a.hideBalloonTime)
    }, cleanChart: function () {
    }, hideBalloonReal: function () {
        var a = this.balloon;
        a && a.hide()
    }, showBalloon: function (a, b, c, d, f) {
        var e = this;
        clearTimeout(e.balloonTO);
        clearInterval(e.hoverInt);
        e.balloonTO = setTimeout(function () {
            e.showBalloonReal.call(e, a, b, c, d, f)
        }, 1)
    }, showBalloonReal: function (a, b, c, d, f) {
        this.handleMouseMove();
        var e =
            this.balloon;
        e.enabled && (e.followCursor(!1), e.changeColor(b), !c || e.fixedPosition ? (e.setPosition(d, f), e.followCursor(!1)) : e.followCursor(!0), a && e.showBalloon(a))
    }, handleTouchMove: function (a) {
        this.hideBalloon();
        var b = this.chartDiv;
        a.touches && (a = a.touches.item(0), this.mouseX = a.pageX - AmCharts.findPosX(b), this.mouseY = a.pageY - AmCharts.findPosY(b))
    }, handleMouseOver: function (a) {
        AmCharts.resetMouseOver();
        this.mouseIsOver = !0
    }, handleMouseOut: function (a) {
        AmCharts.resetMouseOver();
        this.mouseIsOver = !1
    }, handleMouseMove: function (a) {
        if (this.mouseIsOver) {
            var b =
                this.chartDiv;
            a || (a = window.event);
            var c, d;
            if (a) {
                this.posX = AmCharts.findPosX(b);
                this.posY = AmCharts.findPosY(b);
                switch (this.mouseMode) {
                    case 1:
                        c = a.clientX - this.posX;
                        d = a.clientY - this.posY;
                        if (!this.divIsFixed) {
                            var b = document.body, f, e;
                            b && (f = b.scrollLeft, y1 = b.scrollTop);
                            if (b = document.documentElement)e = b.scrollLeft, y2 = b.scrollTop;
                            f = Math.max(f, e);
                            e = Math.max(y1, y2);
                            c += f;
                            d += e
                        }
                        break;
                    case 0:
                        this.divIsFixed ? (c = a.clientX - this.posX, d = a.clientY - this.posY) : (c = a.pageX - this.posX, d = a.pageY - this.posY)
                }
                a.touches && (a = a.touches.item(0),
                    c = a.pageX - this.posX, d = a.pageY - this.posY);
                this.mouseX = c - this.dmouseX;
                this.mouseY = d - this.dmouseY
            }
        }
    }, handleTouchStart: function (a) {
        this.handleMouseDown(a)
    }, handleTouchEnd: function (a) {
        AmCharts.resetMouseOver();
        this.handleReleaseOutside(a)
    }, handleReleaseOutside: function (a) {
    }, handleMouseDown: function (a) {
        AmCharts.resetMouseOver();
        this.mouseIsOver = !0;
        a && a.preventDefault && a.preventDefault()
    }, addLegend: function (a, b) {
        a = AmCharts.processObject(a, AmCharts.AmLegend, this.theme);
        a.divId = b;
        var c;
        c = "object" != typeof b &&
            b ? document.getElementById(b) : b;
        this.legend = a;
        a.chart = this;
        c ? (a.div = c, a.position = "outside", a.autoMargins = !1) : a.div = this.legendDiv;
        c = this.handleLegendEvent;
        this.listenTo(a, "showItem", c);
        this.listenTo(a, "hideItem", c);
        this.listenTo(a, "clickMarker", c);
        this.listenTo(a, "rollOverItem", c);
        this.listenTo(a, "rollOutItem", c);
        this.listenTo(a, "rollOverMarker", c);
        this.listenTo(a, "rollOutMarker", c);
        this.listenTo(a, "clickLabel", c);
        return a
    }, removeLegend: function () {
        this.legend = void 0;
        this.legendDiv.innerHTML = ""
    }, handleResize: function () {
        (AmCharts.isPercents(this.width) ||
            AmCharts.isPercents(this.height)) && this.invalidateSizeReal();
        this.renderFix()
    }, renderFix: function () {
        if (!AmCharts.VML) {
            var a = this.container;
            a && a.renderFix()
        }
    }, getSVG: function () {
        if (AmCharts.hasSVG)return this.container
    }, animate: function (a, b, c, d, f, e, g) {
        a["an_" + b] && AmCharts.removeFromArray(this.animations, a["an_" + b]);
        c = {obj: a, frame: 0, attribute: b, from: c, to: d, time: f, effect: e, suffix: g};
        a["an_" + b] = c;
        this.animations.push(c);
        return c
    }, setLegendData: function (a) {
        var b = this.legend;
        b && b.setData(a)
    }, startInterval: function () {
        var a =
            this;
        clearInterval(a.interval);
        a.interval = setInterval(function () {
            a.updateAnimations.call(a)
        }, AmCharts.updateRate)
    }, stopAnim: function (a) {
        AmCharts.removeFromArray(this.animations, a)
    }, updateAnimations: function () {
        var a;
        this.container && this.container.update();
        for (a = this.animations.length - 1; 0 <= a; a--) {
            var b = this.animations[a], c = 1E3 * b.time / AmCharts.updateRate, d = b.frame + 1, f = b.obj, e = b.attribute;
            if (d <= c) {
                b.frame++;
                var g = Number(b.from), h = Number(b.to) - g, c = AmCharts[b.effect](0, d, g, h, c);
                0 === h ? this.animations.splice(a,
                    1) : f.node.style[e] = c + b.suffix
            } else f.node.style[e] = Number(b.to) + b.suffix, this.animations.splice(a, 1)
        }
    }, brr: function () {
        var a = window.location.hostname.split("."), b;
        2 <= a.length && (b = a[a.length - 2] + "." + a[a.length - 1]);
        this.amLink && (a = this.amLink.parentNode) && a.removeChild(this.amLink);
        a = this.creditsPosition;
        if ("amcharts.com" != b) {
            var c = b = 0, d = this.realWidth, f = this.realHeight;
            if ("serial" == this.type || "xy" == this.type)b = this.marginLeftReal, c = this.marginTopReal, d = b + this.plotAreaWidth, f = c + this.plotAreaHeight;
            var e =
                "http://www.amcharts.com/javascript-charts/", g = "JavaScript charts", h = "JS chart by amCharts";
            "ammap" == this.product && (e = "http://www.ammap.com/javascript-maps/", g = "Interactive JavaScript maps", h = "JS map by amCharts");
            var k = document.createElement("a"), h = document.createTextNode(h);
            k.setAttribute("href", e);
            k.setAttribute("title", g);
            k.appendChild(h);
            this.chartDiv.appendChild(k);
            this.amLink = k;
            e = k.style;
            e.position = "absolute";
            e.textDecoration = "none";
            e.color = this.color;
            e.fontFamily = this.fontFamily;
            e.fontSize =
                this.fontSize + "px";
            e.opacity = 0.7;
            e.display = "block";
            var g = k.offsetWidth, k = k.offsetHeight, h = 5 + b, l = c + 5;
            "bottom-left" == a && (h = 5 + b, l = f - k - 3);
            "bottom-right" == a && (h = d - g - 5, l = f - k - 3);
            "top-right" == a && (h = d - g - 5, l = c + 5);
            e.left = h + "px";
            e.top = l + "px"
        }
    }});
AmCharts.Slice = AmCharts.Class({construct: function () {
}});
AmCharts.SerialDataItem = AmCharts.Class({construct: function () {
}});
AmCharts.GraphDataItem = AmCharts.Class({construct: function () {
}});
AmCharts.Guide = AmCharts.Class({construct: function (a) {
    this.cname = "Guide";
    AmCharts.applyTheme(this, a, this.cname)
}});
AmCharts.AmGraph = AmCharts.Class({construct: function (a) {
    this.cname = "AmGraph";
    this.createEvents("rollOverGraphItem", "rollOutGraphItem", "clickGraphItem", "doubleClickGraphItem", "rightClickGraphItem", "clickGraph", "rollOverGraph", "rollOutGraph");
    this.type = "line";
    this.stackable = !0;
    this.columnCount = 1;
    this.columnIndex = 0;
    this.centerCustomBullets = this.showBalloon = !0;
    this.maxBulletSize = 50;
    this.minBulletSize = 0;
    this.balloonText = "[[value]]";
    this.hidden = this.scrollbar = this.animationPlayed = !1;
    this.pointPosition = "middle";
    this.depthCount = 1;
    this.includeInMinMax = !0;
    this.negativeBase = 0;
    this.visibleInLegend = !0;
    this.showAllValueLabels = !1;
    this.showBulletsAt = this.showBalloonAt = "close";
    this.lineThickness = 1;
    this.dashLength = 0;
    this.connect = !0;
    this.lineAlpha = 1;
    this.bullet = "none";
    this.bulletBorderThickness = 2;
    this.bulletBorderAlpha = 0;
    this.bulletAlpha = 1;
    this.bulletSize = 8;
    this.hideBulletsCount = this.bulletOffset = 0;
    this.labelPosition = "top";
    this.cornerRadiusTop = 0;
    this.cursorBulletAlpha = 1;
    this.gradientOrientation = "vertical";
    this.dy = this.dx =
        0;
    this.periodValue = "";
    this.clustered = !0;
    this.periodSpan = 1;
    this.y = this.x = 0;
    this.minDistance = 1;
    AmCharts.applyTheme(this, a, this.cname)
}, draw: function () {
    var a = this.chart, b = a.container;
    this.container = b;
    this.destroy();
    var c = b.set(), d = b.set();
    this.behindColumns ? (a.graphsBehindSet.push(c), a.bulletBehindSet.push(d)) : (a.graphsSet.push(c), a.bulletSet.push(d));
    var f = this.bulletAxis;
    AmCharts.isString(f) && (this.bulletAxis = a.getValueAxisById(f));
    this.bulletSet = d;
    this.scrollbar || (f = a.marginLeftReal, a = a.marginTopReal,
        c.translate(f, a), d.translate(f, a));
    b = b.set();
    AmCharts.remove(this.columnsSet);
    c.push(b);
    this.set = c;
    this.columnsSet = b;
    this.columnsArray = [];
    this.ownColumns = [];
    this.allBullets = [];
    this.animationArray = [];
    AmCharts.ifArray(this.data) && (c = !1, "xy" == this.chart.type ? this.xAxis.axisCreated && this.yAxis.axisCreated && (c = !0) : this.valueAxis.axisCreated && (c = !0), !this.hidden && c && this.createGraph())
}, createGraph: function () {
    var a = this, b = a.chart;
    "inside" == a.labelPosition && "column" != a.type && (a.labelPosition = "bottom");
    a.startAlpha =
        b.startAlpha;
    a.seqAn = b.sequencedAnimation;
    a.baseCoord = a.valueAxis.baseCoord;
    void 0 === a.fillAlphas && (a.fillAlphas = 0);
    a.bulletColorR = a.bulletColor;
    void 0 === a.bulletColorR && (a.bulletColorR = a.lineColorR, a.bulletColorNegative = a.negativeLineColor);
    void 0 === a.bulletAlpha && (a.bulletAlpha = a.lineAlpha);
    clearTimeout(a.playedTO);
    if (!isNaN(a.valueAxis.min) && !isNaN(a.valueAxis.max)) {
        switch (b.type) {
            case "serial":
                a.categoryAxis && (a.createSerialGraph(), "candlestick" == a.type && 1 > a.valueAxis.minMaxMultiplier && a.positiveClip(a.set));
                break;
            case "radar":
                a.createRadarGraph();
                break;
            case "xy":
                a.createXYGraph(), a.positiveClip(a.set)
        }
        a.playedTO = setTimeout(function () {
            a.setAnimationPlayed.call(a)
        }, 500 * a.chart.startDuration)
    }
}, setAnimationPlayed: function () {
    this.animationPlayed = !0
}, createXYGraph: function () {
    var a = [], b = [], c = this.xAxis, d = this.yAxis;
    this.pmh = d.viH + 1;
    this.pmw = c.viW + 1;
    this.pmy = this.pmx = 0;
    var f;
    for (f = this.start; f <= this.end; f++) {
        var e = this.data[f].axes[c.id].graphs[this.id], g = e.values, h = g.x, k = g.y, g = c.getCoordinate(h), l = d.getCoordinate(k);
        !isNaN(h) && !isNaN(k) && (a.push(g), b.push(l), (h = this.createBullet(e, g, l, f)) || (h = 0), k = this.labelText) && (e = this.createLabel(e, g, l, k), this.allBullets.push(e), this.positionLabel(g, l, e, this.labelPosition, h))
    }
    this.drawLineGraph(a, b);
    this.launchAnimation()
}, createRadarGraph: function () {
    var a = this.valueAxis.stackType, b = [], c = [], d, f, e;
    for (e = this.start; e <= this.end; e++) {
        var g = this.data[e].axes[this.valueAxis.id].graphs[this.id], h;
        h = "none" == a || "3d" == a ? g.values.value : g.values.close;
        if (isNaN(h))this.drawLineGraph(b,
            c), b = [], c = []; else {
            var k = this.y - (this.valueAxis.getCoordinate(h) - this.height), l = 180 - 360 / (this.end - this.start + 1) * e;
            h = k * Math.sin(l / 180 * Math.PI);
            k *= Math.cos(l / 180 * Math.PI);
            b.push(h);
            c.push(k);
            (l = this.createBullet(g, h, k, e)) || (l = 0);
            var m = this.labelText;
            m && (g = this.createLabel(g, h, k, m), this.allBullets.push(g), this.positionLabel(h, k, g, this.labelPosition, l));
            isNaN(d) && (d = h);
            isNaN(f) && (f = k)
        }
    }
    b.push(d);
    c.push(f);
    this.drawLineGraph(b, c);
    this.launchAnimation()
}, positionLabel: function (a, b, c, d, f) {
    var e = c.getBBox();
    switch (d) {
        case "left":
            a -= (e.width + f) / 2 + 2;
            break;
        case "top":
            b -= (f + e.height) / 2 + 1;
            break;
        case "right":
            a += (e.width + f) / 2 + 2;
            break;
        case "bottom":
            b += (f + e.height) / 2 + 1
    }
    c.translate(a, b)
}, getGradRotation: function () {
    var a = 270;
    "horizontal" == this.gradientOrientation && (a = 0);
    return this.gradientRotation = a
}, createSerialGraph: function () {
    this.dashLengthSwitched = this.fillColorsSwitched = this.lineColorSwitched = void 0;
    var a = this.chart, b = this.id, c = this.index, d = this.data, f = this.chart.container, e = this.valueAxis, g = this.type, h =
        this.columnWidthReal, k = this.showBulletsAt;
    isNaN(this.columnWidth) || (h = this.columnWidth);
    isNaN(h) && (h = 0.8);
    var l = this.width, m = this.height, p = this.y, n = this.rotate, q = this.columnCount, s = AmCharts.toCoordinate(this.cornerRadiusTop, h / 2), r = this.connect, u = [], v = [], t, w, z, F, y = this.chart.graphs.length, B, G = this.dx / this.depthCount, K = this.dy / this.depthCount, A = e.stackType, S = this.labelPosition, T = this.start, ca = this.end, U = this.scrollbar, Na = this.categoryAxis, ga = this.baseCoord, ma = this.negativeBase, Q = this.columnIndex, V =
        this.lineThickness, $ = this.lineAlpha, ra = this.lineColorR, N = this.dashLength, W = this.set, pa = S, H = this.getGradRotation(), E = this.chart.columnSpacing, R = Na.cellWidth, da = (R * h - q) / q;
    E > da && (E = da);
    var ha, x, Wa, eb = m + 1, fb = l + 1, Xa = 0, gb = 0, hb, ib, Ya, Za, Ob = this.fillColorsR, Oa = this.negativeFillColors, Da = this.negativeLineColor, Pa = this.fillAlphas, Qa = this.negativeFillAlphas;
    "object" == typeof Pa && (Pa = Pa[0]);
    "object" == typeof Qa && (Qa = Qa[0]);
    var $a = e.getCoordinate(e.min);
    e.logarithmic && ($a = e.getCoordinate(e.minReal));
    this.minCoord =
        $a;
    this.resetBullet && (this.bullet = "none");
    if (!U && ("line" == g || "smoothedLine" == g || "step" == g) && (1 == d.length && "step" != g && "none" == this.bullet && (this.bullet = "round", this.resetBullet = !0), Oa || void 0 != Da)) {
        var Ha = ma;
        Ha > e.max && (Ha = e.max);
        Ha < e.min && (Ha = e.min);
        e.logarithmic && (Ha = e.minReal);
        var ya = e.getCoordinate(Ha), yb = e.getCoordinate(e.max);
        n ? (eb = m, fb = Math.abs(yb - ya), hb = m, ib = Math.abs($a - ya), Za = gb = 0, e.reversed ? (Xa = 0, Ya = ya) : (Xa = ya, Ya = 0)) : (fb = l, eb = Math.abs(yb - ya), ib = l, hb = Math.abs($a - ya), Ya = Xa = 0, e.reversed ? (Za =
            p, gb = ya) : Za = ya + 1)
    }
    var za = Math.round;
    this.pmx = za(Xa);
    this.pmy = za(gb);
    this.pmh = za(eb);
    this.pmw = za(fb);
    this.nmx = za(Ya);
    this.nmy = za(Za);
    this.nmh = za(hb);
    this.nmw = za(ib);
    AmCharts.isModern || (this.nmy = this.nmx = 0, this.nmh = this.height);
    h = "column" == g ? (R * h - E * (q - 1)) / q : R * h;
    1 > h && (h = 1);
    var I;
    if ("line" == g || "step" == g || "smoothedLine" == g) {
        if (0 < T) {
            for (I = T - 1; -1 < I; I--)if (ha = d[I], x = ha.axes[e.id].graphs[b], Wa = x.values.value, !isNaN(Wa)) {
                T = I;
                break
            }
            if (this.lineColorField)for (I = T; -1 < I; I--)if (ha = d[I], x = ha.axes[e.id].graphs[b],
                x.lineColor) {
                this.bulletColorSwitched = this.lineColorSwitched = x.lineColor;
                break
            }
            if (this.fillColorsField)for (I = T; -1 < I; I--)if (ha = d[I], x = ha.axes[e.id].graphs[b], x.fillColors) {
                this.fillColorsSwitched = x.fillColors;
                break
            }
            if (this.dashLengthField)for (I = T; -1 < I; I--)if (ha = d[I], x = ha.axes[e.id].graphs[b], !isNaN(x.dashLength)) {
                this.dashLengthSwitched = x.dashLength;
                break
            }
        }
        if (ca < d.length - 1)for (I = ca + 1; I < d.length; I++)if (ha = d[I], x = ha.axes[e.id].graphs[b], Wa = x.values.value, !isNaN(Wa)) {
            ca = I;
            break
        }
    }
    ca < d.length - 1 && ca++;
    var X =
        [], Y = [], Ea = !1;
    if ("line" == g || "step" == g || "smoothedLine" == g)if (this.stackable && "regular" == A || "100%" == A || this.fillToGraph)Ea = !0;
    var zb = this.noStepRisers, ab = -1E3, bb = -1E3, cb = this.minDistance;
    for (I = T; I <= ca; I++) {
        ha = d[I];
        x = ha.axes[e.id].graphs[b];
        x.index = I;
        var O, P, M, aa, ia = NaN, D = NaN, C = NaN, L = NaN, J = NaN, Ia = NaN, Aa = NaN, Ja = NaN, Ba = NaN, ba = NaN, fa = NaN, ja = NaN, ka = NaN, Z = NaN, jb = NaN, kb = NaN, na = NaN, qa = void 0, Ca = Ob, Ra = Pa, sa = ra, oa, ta, Sa = this.pattern;
        void 0 != x.pattern && (Sa = x.pattern);
        void 0 != x.color && (Ca = x.color);
        x.fillColors &&
        (Ca = x.fillColors);
        isNaN(x.alpha) || (Ra = x.alpha);
        isNaN(x.dashLength) || (N = x.dashLength);
        var ua = x.values;
        e.recalculateToPercents && (ua = x.percents);
        if (ua) {
            Z = this.stackable && "none" != A && "3d" != A ? ua.close : ua.value;
            if ("candlestick" == g || "ohlc" == g)Z = ua.close, kb = ua.low, Aa = e.getCoordinate(kb), jb = ua.high, Ba = e.getCoordinate(jb);
            na = ua.open;
            C = e.getCoordinate(Z);
            isNaN(na) || (J = e.getCoordinate(na));
            if (!U)switch (this.showBalloonAt) {
                case "close":
                    x.y = C;
                    break;
                case "open":
                    x.y = J;
                    break;
                case "high":
                    x.y = Ba;
                    break;
                case "low":
                    x.y =
                        Aa
            }
            var ia = ha.x[Na.id], Ka = this.periodSpan - 1, la = Math.floor(R / 2) + Math.floor(Ka * R / 2), va = la, Ab = 0;
            "left" == this.stepDirection && (Ab = (2 * R + Ka * R) / 2, ia -= Ab);
            "start" == this.pointPosition && (ia -= R / 2 + Math.floor(Ka * R / 2), la = 0, va = Math.floor(R) + Math.floor(Ka * R));
            "end" == this.pointPosition && (ia += R / 2 + Math.floor(Ka * R / 2), la = Math.floor(R) + Math.floor(Ka * R), va = 0);
            if (zb) {
                var lb = this.columnWidth;
                isNaN(lb) || (la *= lb, va *= lb)
            }
            U || (x.x = ia);
            -1E5 > ia && (ia = -1E5);
            ia > l + 1E5 && (ia = l + 1E5);
            n ? (D = C, L = J, J = C = ia, isNaN(na) && !this.fillToGraph && (L = ga),
                Ia = Aa, Ja = Ba) : (L = D = ia, isNaN(na) && !this.fillToGraph && (J = ga));
            Z < na && (x.isNegative = !0, Oa && (Ca = Oa), Qa && (Ra = Qa), void 0 != Da && (sa = Da));
            switch (g) {
                case "line":
                    if (isNaN(Z))r || (this.drawLineGraph(u, v, X, Y), u = [], v = [], X = [], Y = []); else {
                        x.isNegative = Z < ma ? !0 : !1;
                        if (Math.abs(D - ab) >= cb || Math.abs(C - bb) >= cb)u.push(D), v.push(C), ab = D, bb = C;
                        ba = D;
                        fa = C;
                        ja = D;
                        ka = C;
                        !Ea || isNaN(J) || isNaN(L) || (X.push(L), Y.push(J));
                        void 0 == x.lineColor && void 0 == x.fillColors && isNaN(x.dashLength) || (this.drawLineGraph(u, v, X, Y), u = [D], v = [C], X = [], Y = [], !Ea ||
                            isNaN(J) || isNaN(L) || (X.push(L), Y.push(J)), this.lineColorSwitched = x.lineColor, this.fillColorsSwitched = x.fillColors, this.dashLengthSwitched = x.dashLength)
                    }
                    break;
                case "smoothedLine":
                    if (isNaN(Z))r || (this.drawSmoothedGraph(u, v, X, Y), u = [], v = [], X = [], Y = []); else {
                        x.isNegative = Z < ma ? !0 : !1;
                        if (Math.abs(D - ab) >= cb || Math.abs(C - bb) >= cb)u.push(D), v.push(C), ab = D, bb = C;
                        ba = D;
                        fa = C;
                        ja = D;
                        ka = C;
                        !Ea || isNaN(J) || isNaN(L) || (X.push(L), Y.push(J));
                        void 0 == x.lineColor && void 0 == x.fillColors && isNaN(x.dashLength) || (this.drawSmoothedGraph(u,
                            v, X, Y), u = [D], v = [C], X = [], Y = [], !Ea || isNaN(J) || isNaN(L) || (X.push(L), Y.push(J)), this.lineColorSwitched = x.lineColor, this.fillColorsSwitched = x.fillColors, this.dashLengthSwitched = x.dashLength)
                    }
                    break;
                case "step":
                    if (!isNaN(Z))x.isNegative = Z < ma ? !0 : !1, void 0 == x.lineColor && void 0 == x.fillColors && isNaN(x.dashLength) || (this.drawLineGraph(u, v, X, Y), u = [], v = [], X = [], Y = [], this.lineColorSwitched = x.lineColor, this.fillColorsSwitched = x.fillColors, this.dashLengthSwitched = x.dashLength), n ? (isNaN(t) || (u.push(t), v.push(C - la)),
                        v.push(C - la), u.push(D), v.push(C + va), u.push(D), !Ea || isNaN(J) || isNaN(L) || (X.push(z), Y.push(J - la), X.push(L), Y.push(J - la), X.push(L), Y.push(J + va))) : (isNaN(w) || (v.push(w), u.push(t), v.push(w), u.push(D - la)), u.push(D - la), v.push(C), u.push(D + va), v.push(C), !Ea || isNaN(J) || isNaN(L) || (X.push(L - la), Y.push(F), X.push(L - la), Y.push(J), X.push(L + va), Y.push(J))), t = D, w = C, z = L, F = J, ba = D, fa = C, ja = D, ka = C, zb && (t = w = NaN, this.drawLineGraph(u, v, X, Y), u = [], v = [], X = [], Y = []); else if (!r) {
                        if (1 >= this.periodSpan || 1 < this.periodSpan && D - t > la +
                            va)t = w = NaN;
                        this.drawLineGraph(u, v, X, Y);
                        u = [];
                        v = [];
                        X = [];
                        Y = []
                    }
                    break;
                case "column":
                    oa = sa;
                    void 0 != x.lineColor && (oa = x.lineColor);
                    if (!isNaN(Z)) {
                        Z < ma ? (x.isNegative = !0, Oa && (Ca = Oa), void 0 != Da && (oa = Da)) : x.isNegative = !1;
                        var Bb = e.min, Cb = e.max;
                        if (!(Z < Bb && na < Bb || Z > Cb && na > Cb))if (n) {
                            "3d" == A ? (P = C - 0.5 * (h + E) + E / 2 + K * Q, O = L + G * Q) : (P = Math.floor(C - (q / 2 - Q) * (h + E) + E / 2), O = L);
                            M = h;
                            ba = D;
                            fa = P + h / 2;
                            ja = D;
                            ka = P + h / 2;
                            P + M > m && (M = m - P);
                            0 > P && (M += P, P = 0);
                            aa = D - L;
                            var Pb = O;
                            O = AmCharts.fitToBounds(O, 0, l);
                            aa += Pb - O;
                            aa = AmCharts.fitToBounds(aa, -O, l - O + G *
                                Q);
                            if (P < m && 0 < M && (qa = new AmCharts.Cuboid(f, aa, M, G - a.d3x, K - a.d3y, Ca, Ra, V, oa, $, H, s, n, N, Sa), "bottom" != S && "inside" != S && "middle" != S))if (S = e.reversed ? "left" : "right", 0 > Z)S = e.reversed ? "right" : "left"; else if ("regular" == A || "100%" == A)ba += this.dx
                        } else {
                            "3d" == A ? (O = D - 0.5 * (h + E) + E / 2 + G * Q, P = J + K * Q) : (O = D - (q / 2 - Q) * (h + E) + E / 2, P = J);
                            M = h;
                            ba = O + h / 2;
                            fa = C;
                            ja = O + h / 2;
                            ka = C;
                            O + M > l + Q * G && (M = l - O + Q * G);
                            0 > O && (M += O, O = 0);
                            aa = C - J;
                            var Qb = P;
                            P = AmCharts.fitToBounds(P, this.dy, m);
                            aa += Qb - P;
                            aa = AmCharts.fitToBounds(aa, -P + K * Q, m - P);
                            if (O < l + Q * G && 0 < M)if (qa = new AmCharts.Cuboid(f,
                                M, aa, G - a.d3x, K - a.d3y, Ca, Ra, V, oa, this.lineAlpha, H, s, n, N, Sa), 0 > Z && "middle" != S && "inside" != S)S = "bottom"; else if (S = pa, "regular" == A || "100%" == A)fa += this.dy
                        }
                        if (qa && (ta = qa.set, ta.translate(O, P), this.columnsSet.push(ta), (x.url || this.showHandOnHover) && ta.setAttr("cursor", "pointer"), !U)) {
                            "none" == A && (B = n ? (this.end + 1 - I) * y - c : y * I + c);
                            "3d" == A && (n ? (B = (y - c) * (this.end + 1 - I), ba += G * this.columnIndex, ja += G * this.columnIndex, x.y += G * this.columnIndex) : (B = (y - c) * (I + 1), ba += 3, fa += K * this.columnIndex + 7, ka += K * this.columnIndex, x.y += K *
                                this.columnIndex));
                            if ("regular" == A || "100%" == A)"inside" != S && (S = "middle"), B = n ? 0 < ua.value ? (this.end + 1 - I) * y + c : (this.end + 1 - I) * y - c : 0 < ua.value ? y * I + c : y * I - c;
                            this.columnsArray.push({column: qa, depth: B});
                            x.x = n ? P + M / 2 : O + M / 2;
                            this.ownColumns.push(qa);
                            this.animateColumns(qa, I, D, L, C, J);
                            this.addListeners(ta, x)
                        }
                    }
                    break;
                case "candlestick":
                    if (!isNaN(na) && !isNaN(Z)) {
                        var db, mb;
                        oa = sa;
                        void 0 != x.lineColor && (oa = x.lineColor);
                        if (n) {
                            if (P = C - h / 2, O = L, M = h, P + M > m && (M = m - P), 0 > P && (M += P, P = 0), P < m && 0 < M) {
                                var nb, ob;
                                Z > na ? (nb = [D, Ja], ob = [L, Ia]) :
                                    (nb = [L, Ja], ob = [D, Ia]);
                                !isNaN(Ja) && !isNaN(Ia) && C < m && 0 < C && (db = AmCharts.line(f, nb, [C, C], oa, $, V), mb = AmCharts.line(f, ob, [C, C], oa, $, V));
                                aa = D - L;
                                qa = new AmCharts.Cuboid(f, aa, M, G, K, Ca, Pa, V, oa, $, H, s, n, N, Sa)
                            }
                        } else if (O = D - h / 2, P = J + V / 2, M = h, O + M > l && (M = l - O), 0 > O && (M += O, O = 0), aa = C - J, O < l && 0 < M) {
                            var qa = new AmCharts.Cuboid(f, M, aa, G, K, Ca, Ra, V, oa, $, H, s, n, N, Sa), pb, qb;
                            Z > na ? (pb = [C, Ba], qb = [J, Aa]) : (pb = [J, Ba], qb = [C, Aa]);
                            !isNaN(Ba) && !isNaN(Aa) && D < l && 0 < D && (db = AmCharts.line(f, [D, D], pb, oa, $, V), mb = AmCharts.line(f, [D, D], qb, oa, $, V))
                        }
                        qa &&
                        (ta = qa.set, W.push(ta), ta.translate(O, P - V / 2), (x.url || this.showHandOnHover) && ta.setAttr("cursor", "pointer"), db && (W.push(db), W.push(mb)), ba = D, fa = C, n ? (ka = C, ja = D, "open" == k && (ja = L), "high" == k && (ja = Ja), "low" == k && (ja = Ia)) : (ka = C, "open" == k && (ka = J), "high" == k && (ka = Ba), "low" == k && (ka = Aa), ja = D), U || (x.x = n ? P + M / 2 : O + M / 2, this.animateColumns(qa, I, D, L, C, J), this.addListeners(ta, x)))
                    }
                    break;
                case "ohlc":
                    if (!(isNaN(na) || isNaN(jb) || isNaN(kb) || isNaN(Z))) {
                        Z < na && (x.isNegative = !0, void 0 != Da && (sa = Da));
                        var rb, sb, tb;
                        if (n) {
                            var ub = C -
                                h / 2, ub = AmCharts.fitToBounds(ub, 0, m), Db = AmCharts.fitToBounds(C, 0, m), vb = C + h / 2, vb = AmCharts.fitToBounds(vb, 0, m);
                            sb = AmCharts.line(f, [L, L], [ub, Db], sa, $, V, N);
                            0 < C && C < m && (rb = AmCharts.line(f, [Ia, Ja], [C, C], sa, $, V, N));
                            tb = AmCharts.line(f, [D, D], [Db, vb], sa, $, V, N)
                        } else {
                            var wb = D - h / 2, wb = AmCharts.fitToBounds(wb, 0, l), Eb = AmCharts.fitToBounds(D, 0, l), xb = D + h / 2, xb = AmCharts.fitToBounds(xb, 0, l);
                            sb = AmCharts.line(f, [wb, Eb], [J, J], sa, $, V, N);
                            0 < D && D < l && (rb = AmCharts.line(f, [D, D], [Aa, Ba], sa, $, V, N));
                            tb = AmCharts.line(f, [Eb, xb], [C, C],
                                sa, $, V, N)
                        }
                        W.push(sb);
                        W.push(rb);
                        W.push(tb);
                        ba = D;
                        fa = C;
                        ja = D;
                        ka = C
                    }
            }
            if (!U && !isNaN(Z)) {
                var Fb = this.hideBulletsCount;
                if (this.end - this.start <= Fb || 0 === Fb) {
                    var Fa = this.createBullet(x, ja, ka, I);
                    Fa || (Fa = 0);
                    var Gb = this.labelText;
                    if (Gb) {
                        var ea = this.createLabel(x, 0, 0, Gb), wa = 0, xa = 0, Hb = ea.getBBox(), La = Hb.width, Ga = Hb.height;
                        switch (S) {
                            case "left":
                                wa = -(La / 2 + Fa / 2 + 3);
                                break;
                            case "top":
                                xa = -(Ga / 2 + Fa / 2 + 3);
                                break;
                            case "right":
                                wa = Fa / 2 + 2 + La / 2;
                                break;
                            case "bottom":
                                n && "column" == g ? (ba = ga, 0 > Z || 0 < Z && e.reversed ? (wa = -6, ea.attr({"text-anchor": "end"})) :
                                    (wa = 6, ea.attr({"text-anchor": "start"}))) : (xa = Fa / 2 + Ga / 2, ea.x = -(La / 2 + 2));
                                break;
                            case "middle":
                                "column" == g && (n ? (xa = -(Ga / 2) + this.fontSize / 2, wa = -(D - L) / 2 - G, 0 > aa && (wa += G), Math.abs(D - L) < La && !this.showAllValueLabels && (ea.remove(), ea = null)) : (xa = -(C - J) / 2, 0 > aa && (xa -= K), Math.abs(C - J) < Ga && !this.showAllValueLabels && (ea.remove(), ea = null)));
                                break;
                            case "inside":
                                n ? (xa = -(Ga / 2) + this.fontSize / 2, wa = 0 > aa ? La / 2 + 6 : -La / 2 - 6) : xa = 0 > aa ? Ga : -Ga
                        }
                        if (ea) {
                            if (isNaN(fa) || isNaN(ba))ea.remove(), ea = null; else if (ba += wa, fa += xa, ea.translate(ba,
                                fa), n) {
                                if (0 > fa || fa > m)ea.remove(), ea = null
                            } else {
                                var Ib = 0;
                                "3d" == A && (Ib = G * Q);
                                if (0 > ba || ba > l + Ib)ea.remove(), ea = null
                            }
                            ea && this.allBullets.push(ea)
                        }
                    }
                    if ("regular" == A || "100%" == A) {
                        var Jb = e.totalText;
                        if (Jb) {
                            var Ma = this.createLabel(x, 0, 0, Jb, e.totalTextColor);
                            this.allBullets.push(Ma);
                            var Kb = Ma.getBBox(), Lb = Kb.width, Mb = Kb.height, Ta, Ua, Nb = e.totals[I];
                            Nb && Nb.remove();
                            var Va = 0;
                            "column" != g && (Va = Fa);
                            n ? (Ua = C, Ta = 0 > Z ? D - Lb / 2 - 2 - Va : D + Lb / 2 + 3 + Va) : (Ta = D, Ua = 0 > Z ? C + Mb / 2 + Va : C - Mb / 2 - 3 - Va);
                            Ma.translate(Ta, Ua);
                            e.totals[I] = Ma;
                            n ? (0 > Ua ||
                                Ua > m) && Ma.remove() : (0 > Ta || Ta > l) && Ma.remove()
                        }
                    }
                }
            }
        }
    }
    if ("line" == g || "step" == g || "smoothedLine" == g)"smoothedLine" == g ? this.drawSmoothedGraph(u, v, X, Y) : this.drawLineGraph(u, v, X, Y), U || this.launchAnimation();
    this.bulletsHidden && this.hideBullets()
}, animateColumns: function (a, b, c, d, f, e) {
    var g = this;
    c = g.chart.startDuration;
    0 < c && !g.animationPlayed && (g.seqAn ? (a.set.hide(), g.animationArray.push(a), a = setTimeout(function () {
        g.animate.call(g)
    }, c / (g.end - g.start + 1) * (b - g.start) * 1E3), g.timeOuts.push(a)) : g.animate(a))
}, createLabel: function (a, b, c, d, f) {
    var e = this.chart, g = a.labelColor;
    g || (g = this.color);
    g || (g = e.color);
    f && (g = f);
    f = this.fontSize;
    void 0 === f && (this.fontSize = f = e.fontSize);
    a = e.formatString(d, a);
    a = AmCharts.cleanFromEmpty(a);
    e = AmCharts.text(this.container, a, g, e.fontFamily, f);
    e.translate(b, c);
    this.bulletSet.push(e);
    return e
}, positiveClip: function (a) {
    a.clipRect(this.pmx, this.pmy, this.pmw, this.pmh)
}, negativeClip: function (a) {
    a.clipRect(this.nmx, this.nmy, this.nmw, this.nmh)
}, drawLineGraph: function (a, b, c, d) {
    var f = this;
    if (1 < a.length) {
        var e =
            f.set, g = f.container, h = g.set(), k = g.set();
        e.push(k);
        e.push(h);
        var l = f.lineAlpha, m = f.lineThickness, e = f.fillAlphas, p = f.lineColorR, n = f.negativeLineAlpha;
        isNaN(n) && (n = l);
        var q = f.lineColorSwitched;
        q && (p = q);
        var q = f.fillColorsR, s = f.fillColorsSwitched;
        s && (q = s);
        var r = f.dashLength;
        (s = f.dashLengthSwitched) && (r = s);
        var s = f.negativeLineColor, u = f.negativeFillColors, v = f.negativeFillAlphas, t = f.baseCoord;
        0 !== f.negativeBase && (t = f.valueAxis.getCoordinate(f.negativeBase));
        l = AmCharts.line(g, a, b, p, l, m, r, !1, !0);
        h.push(l);
        h.click(function (a) {
            f.handleGraphEvent(a, "clickGraph")
        }).mouseover(function (a) {
            f.handleGraphEvent(a, "rollOverGraph")
        }).mouseout(function (a) {
            f.handleGraphEvent(a, "rollOutGraph")
        });
        void 0 !== s && (m = AmCharts.line(g, a, b, s, n, m, r, !1, !0), k.push(m));
        if (0 < e || 0 < v)if (m = a.join(";").split(";"), n = b.join(";").split(";"), "serial" == f.chart.type && (0 < c.length ? (c.reverse(), d.reverse(), m = a.concat(c), n = b.concat(d)) : f.rotate ? (n.push(n[n.length - 1]), m.push(t), n.push(n[0]), m.push(t), n.push(n[0]), m.push(m[0])) : (m.push(m[m.length -
            1]), n.push(t), m.push(m[0]), n.push(t), m.push(a[0]), n.push(n[0]))), a = f.gradientRotation, 0 < e && (b = AmCharts.polygon(g, m, n, q, e, 1, "#000", 0, a), b.pattern(f.pattern), h.push(b)), u || void 0 !== s)isNaN(v) && (v = e), u || (u = s), g = AmCharts.polygon(g, m, n, u, v, 1, "#000", 0, a), g.pattern(f.pattern), k.push(g), k.click(function (a) {
            f.handleGraphEvent(a, "clickGraph")
        }).mouseover(function (a) {
            f.handleGraphEvent(a, "rollOverGraph")
        }).mouseout(function (a) {
            f.handleGraphEvent(a, "rollOutGraph")
        });
        f.applyMask(k, h)
    }
}, applyMask: function (a, b) {
    var c =
        a.length();
    "serial" != this.chart.type || this.scrollbar || (this.positiveClip(b), 0 < c && this.negativeClip(a))
}, drawSmoothedGraph: function (a, b, c, d) {
    if (1 < a.length) {
        var f = this.set, e = this.container, g = e.set(), h = e.set();
        f.push(h);
        f.push(g);
        var k = this.lineAlpha, l = this.lineThickness, f = this.dashLength, m = this.fillAlphas, p = this.lineColorR, n = this.fillColorsR, q = this.negativeLineColor, s = this.negativeFillColors, r = this.negativeFillAlphas, u = this.baseCoord, v = this.lineColorSwitched;
        v && (p = v);
        (v = this.fillColorsSwitched) && (n =
            v);
        v = this.negativeLineAlpha;
        isNaN(v) && (v = k);
        k = new AmCharts.Bezier(e, a, b, p, k, l, n, 0, f);
        g.push(k.path);
        void 0 !== q && (l = new AmCharts.Bezier(e, a, b, q, v, l, n, 0, f), h.push(l.path));
        0 < m && (k = a.join(";").split(";"), p = b.join(";").split(";"), l = "", 0 < c.length ? (c.push("M"), d.push("M"), c.reverse(), d.reverse(), k = a.concat(c), p = b.concat(d)) : (this.rotate ? (l += " L" + u + "," + b[b.length - 1], l += " L" + u + "," + b[0]) : (l += " L" + a[a.length - 1] + "," + u, l += " L" + a[0] + "," + u), l += " L" + a[0] + "," + b[0]), c = new AmCharts.Bezier(e, k, p, NaN, 0, 0, n, m, f, l), c.path.pattern(this.pattern),
            g.push(c.path), s || void 0 !== q) && (r || (r = m), s || (s = q), a = new AmCharts.Bezier(e, a, b, NaN, 0, 0, s, r, f, l), a.path.pattern(this.pattern), h.push(a.path));
        this.applyMask(h, g)
    }
}, launchAnimation: function () {
    var a = this, b = a.chart.startDuration;
    if (0 < b && !a.animationPlayed) {
        var c = a.set, d = a.bulletSet;
        AmCharts.VML || (c.attr({opacity: a.startAlpha}), d.attr({opacity: a.startAlpha}));
        c.hide();
        d.hide();
        a.seqAn ? (b = setTimeout(function () {
            a.animateGraphs.call(a)
        }, a.index * b * 1E3), a.timeOuts.push(b)) : a.animateGraphs()
    }
}, animateGraphs: function () {
    var a =
        this.chart, b = this.set, c = this.bulletSet, d = this.x, f = this.y;
    b.show();
    c.show();
    var e = a.startDuration, a = a.startEffect;
    b && (this.rotate ? (b.translate(-1E3, f), c.translate(-1E3, f)) : (b.translate(d, -1E3), c.translate(d, -1E3)), b.animate({opacity: 1, translate: d + "," + f}, e, a), c.animate({opacity: 1, translate: d + "," + f}, e, a))
}, animate: function (a) {
    var b = this.chart, c = this.animationArray;
    !a && 0 < c.length && (a = c[0], c.shift());
    c = AmCharts[AmCharts.getEffect(b.startEffect)];
    b = b.startDuration;
    a && (this.rotate ? a.animateWidth(b, c) : a.animateHeight(b,
        c), a.set.show())
}, legendKeyColor: function () {
    var a = this.legendColor, b = this.lineAlpha;
    void 0 === a && (a = this.lineColorR, 0 === b && (b = this.fillColorsR) && (a = "object" == typeof b ? b[0] : b));
    return a
}, legendKeyAlpha: function () {
    var a = this.legendAlpha;
    void 0 === a && (a = this.lineAlpha, this.fillAlphas > a && (a = this.fillAlphas), 0 === a && (a = this.bulletAlpha), 0 === a && (a = 1));
    return a
}, createBullet: function (a, b, c, d) {
    d = this.container;
    var f = this.bulletOffset, e = this.bulletSize;
    isNaN(a.bulletSize) || (e = a.bulletSize);
    var g = a.values.value;
    isNaN(this.maxValue) || isNaN(g) || (e = (g - this.minValue) / (this.maxValue - this.minValue) * (this.maxBulletSize - this.minBulletSize) + this.minBulletSize);
    var h = e;
    this.bulletAxis && (e = a.values.error, isNaN(e) || (g = e), e = this.bulletAxis.stepWidth * g);
    e < this.minBulletSize && (e = this.minBulletSize);
    this.rotate ? b += f : c -= f;
    var k, l = this.bulletColorR;
    a.lineColor && (this.bulletColorSwitched = a.lineColor);
    this.bulletColorSwitched && (l = this.bulletColorSwitched);
    a.isNegative && void 0 !== this.bulletColorNegative && (l = this.bulletColorNegative);
    void 0 !== a.color && (l = a.color);
    var m;
    "xy" == this.chart.type && this.valueField && (m = this.pattern, a.pattern && (m = a.pattern));
    f = this.bullet;
    a.bullet && (f = a.bullet);
    var g = this.bulletBorderThickness, p = this.bulletBorderColorR, n = this.bulletBorderAlpha, q = this.bulletAlpha;
    p || (p = l);
    this.useLineColorForBulletBorder && (p = this.lineColorR);
    var s = a.alpha;
    isNaN(s) || (q = s);
    if ("none" != this.bullet || a.bullet)k = AmCharts.bullet(d, f, e, l, q, g, p, n, h, 0, m);
    if (this.customBullet || a.customBullet)m = this.customBullet, a.customBullet && (m =
        a.customBullet), m && (k && k.remove(), "function" == typeof m ? (k = new m, k.chart = this.chart, a.bulletConfig && (k.availableSpace = c, k.graph = this, a.bulletConfig.minCoord = this.minCoord - c, k.bulletConfig = a.bulletConfig), k.write(d), k = k.set) : (this.chart.path && (m = this.chart.path + m), k = d.set(), d = d.image(m, 0, 0, e, e), k.push(d), this.centerCustomBullets && d.translate(-e / 2, -e / 2)));
    k && ((a.url || this.showHandOnHover) && k.setAttr("cursor", "pointer"), "serial" == this.chart.type && (0 > b - 0 || b - 0 > this.width || c < -e / 2 || c - 0 > this.height) && (k.remove(),
        k = null), k && (this.bulletSet.push(k), k.translate(b, c), this.addListeners(k, a), this.allBullets.push(k)), a.bx = b, a.by = c);
    a.bulletGraphics = k;
    return e
}, showBullets: function () {
    var a = this.allBullets, b;
    this.bulletsHidden = !1;
    for (b = 0; b < a.length; b++)a[b].show()
}, hideBullets: function () {
    var a = this.allBullets, b;
    this.bulletsHidden = !0;
    for (b = 0; b < a.length; b++)a[b].hide()
}, addListeners: function (a, b) {
    var c = this;
    a.mouseover(function (a) {
        c.handleRollOver(b, a)
    }).mouseout(function (a) {
        c.handleRollOut(b, a)
    }).touchend(function (a) {
        c.handleRollOver(b,
            a);
        c.chart.panEventsEnabled && c.handleClick(b, a)
    }).touchstart(function (a) {
        c.handleRollOver(b, a)
    }).click(function (a) {
        c.handleClick(b, a)
    }).dblclick(function (a) {
        c.handleDoubleClick(b, a)
    }).contextmenu(function (a) {
        c.handleRightClick(b, a)
    })
}, handleRollOver: function (a, b) {
    if (a) {
        var c = this.chart, d = {type: "rollOverGraphItem", item: a, index: a.index, graph: this, target: this, chart: this.chart, event: b};
        this.fire("rollOverGraphItem", d);
        c.fire("rollOverGraphItem", d);
        clearTimeout(c.hoverInt);
        d = this.showBalloon;
        c.chartCursor &&
            "serial" == c.type && (d = !1, !c.chartCursor.valueBalloonsEnabled && this.showBalloon && (d = !0));
        if (d) {
            var d = c.formatString(this.balloonText, a, !0), f = this.balloonFunction;
            f && (d = f(a, a.graph));
            d = AmCharts.cleanFromEmpty(d);
            f = c.getBalloonColor(this, a);
            c.balloon.showBullet = !1;
            c.balloon.pointerOrientation = "V";
            var e = a.x, g = a.y;
            c.rotate && (e = a.y, g = a.x);
            c.showBalloon(d, f, !0, e + c.marginLeftReal, g + c.marginTopReal)
        }
    }
    this.handleGraphEvent(b, "rollOverGraph")
}, handleRollOut: function (a, b) {
    this.chart.hideBalloon();
    if (a) {
        var c =
        {type: "rollOutGraphItem", item: a, index: a.index, graph: this, target: this, chart: this.chart, event: b};
        this.fire("rollOutGraphItem", c);
        this.chart.fire("rollOutGraphItem", c)
    }
    this.handleGraphEvent(b, "rollOutGraph")
}, handleClick: function (a, b) {
    if (a) {
        var c = {type: "clickGraphItem", item: a, index: a.index, graph: this, target: this, chart: this.chart, event: b};
        this.fire("clickGraphItem", c);
        this.chart.fire("clickGraphItem", c);
        AmCharts.getURL(a.url, this.urlTarget)
    }
    this.handleGraphEvent(b, "clickGraph")
}, handleGraphEvent: function (a, b) {
    var c = {type: b, graph: this, target: this, chart: this.chart, event: a};
    this.fire(b, c);
    this.chart.fire(b, c)
}, handleRightClick: function (a, b) {
    if (a) {
        var c = {type: "rightClickGraphItem", item: a, index: a.index, graph: this, target: this, chart: this.chart, event: b};
        this.fire("rightClickGraphItem", c);
        this.chart.fire("rightClickGraphItem", c)
    }
}, handleDoubleClick: function (a, b) {
    if (a) {
        var c = {type: "doubleClickGraphItem", item: a, index: a.index, graph: this, target: this, chart: this.chart, event: b};
        this.fire("doubleClickGraphItem", c);
        this.chart.fire("doubleClickGraphItem", c)
    }
}, zoom: function (a, b) {
    this.start = a;
    this.end = b;
    this.draw()
}, changeOpacity: function (a) {
    var b = this.set;
    b && b.setAttr("opacity", a);
    if (b = this.ownColumns) {
        var c;
        for (c = 0; c < b.length; c++) {
            var d = b[c].set;
            d && d.setAttr("opacity", a)
        }
    }
    (b = this.bulletSet) && b.setAttr("opacity", a)
}, destroy: function () {
    AmCharts.remove(this.set);
    AmCharts.remove(this.bulletSet);
    var a = this.timeOuts;
    if (a) {
        var b;
        for (b = 0; b < a.length; b++)clearTimeout(a[b])
    }
    this.timeOuts = []
}});
AmCharts.ChartCursor = AmCharts.Class({construct: function (a) {
    this.cname = "ChartCursor";
    this.createEvents("changed", "zoomed", "onHideCursor", "draw", "selected", "moved");
    this.enabled = !0;
    this.cursorAlpha = 1;
    this.selectionAlpha = 0.2;
    this.cursorColor = "#CC0000";
    this.categoryBalloonAlpha = 1;
    this.color = "#FFFFFF";
    this.type = "cursor";
    this.zoomed = !1;
    this.zoomable = !0;
    this.pan = !1;
    this.categoryBalloonDateFormat = "MMM DD, YYYY";
    this.categoryBalloonEnabled = this.valueBalloonsEnabled = !0;
    this.rolledOver = !1;
    this.cursorPosition =
        "middle";
    this.bulletsEnabled = this.skipZoomDispatch = !1;
    this.bulletSize = 8;
    this.selectWithoutZooming = this.oneBalloonOnly = !1;
    this.graphBulletSize = 1.7;
    this.animationDuration = 0.3;
    this.zooming = !1;
    this.adjustment = 0;
    AmCharts.applyTheme(this, a, this.cname)
}, draw: function () {
    var a = this;
    a.destroy();
    var b = a.chart, c = b.container;
    a.rotate = b.rotate;
    a.container = c;
    c = c.set();
    c.translate(a.x, a.y);
    a.set = c;
    b.cursorSet.push(c);
    c = new AmCharts.AmBalloon;
    c.chart = b;
    a.categoryBalloon = c;
    AmCharts.copyProperties(b.balloon, c);
    c.cornerRadius =
        0;
    c.shadowAlpha = 0;
    c.borderThickness = 1;
    c.borderAlpha = 1;
    c.showBullet = !1;
    var d = a.categoryBalloonColor;
    void 0 === d && (d = a.cursorColor);
    c.fillColor = d;
    c.fillAlpha = a.categoryBalloonAlpha;
    c.borderColor = d;
    c.color = a.color;
    a.rotate && (c.pointerOrientation = "H");
    a.prevX = [];
    a.prevY = [];
    a.prevTX = [];
    a.prevTY = [];
    if (a.valueBalloonsEnabled)for (c = 0; c < b.graphs.length; c++)d = new AmCharts.AmBalloon, d.chart = b, AmCharts.copyProperties(b.balloon, d), b.graphs[c].valueBalloon = d;
    "cursor" == a.type ? a.createCursor() : a.createCrosshair();
    a.interval = setInterval(function () {
        a.detectMovement.call(a)
    }, 40)
}, updateData: function () {
    var a = this.chart;
    this.data = a.chartData;
    this.firstTime = a.firstTime;
    this.lastTime = a.lastTime
}, createCursor: function () {
    var a = this.chart, b = this.cursorAlpha, c = a.categoryAxis, d = c.position, f = c.inside, e = c.axisThickness, g = this.categoryBalloon, h, k, l = a.dx, m = a.dy, p = this.x, n = this.y, q = this.width, s = this.height, a = a.rotate, r = c.tickLength;
    g.pointerWidth = r;
    a ? (h = [0, q, q + l], k = [0, 0, m]) : (h = [l, 0, 0], k = [m, 0, s]);
    this.line = b = AmCharts.line(this.container,
        h, k, this.cursorColor, b, 1);
    this.set.push(b);
    a ? (f && (g.pointerWidth = 0), "right" == d ? f ? g.setBounds(p, n + m, p + q + l, n + s + m) : g.setBounds(p + q + l + e, n + m, p + q + 1E3, n + s + m) : f ? g.setBounds(p, n, q + p, s + n) : g.setBounds(-1E3, -1E3, p - r - e, n + s + 15)) : (g.maxWidth = q, c.parseDates && (r = 0, g.pointerWidth = 0), "top" == d ? f ? g.setBounds(p + l, n + m, q + l + p, s + n) : g.setBounds(p + l, -1E3, q + l + p, n + m - r - e) : f ? g.setBounds(p, n, q + p, s + n - r) : g.setBounds(p, n + s + r + e - 1, p + q, n + s + r + e));
    this.hideCursor()
}, createCrosshair: function () {
    var a = this.cursorAlpha, b = this.container, c = AmCharts.line(b,
        [0, 0], [0, this.height], this.cursorColor, a, 1), a = AmCharts.line(b, [0, this.width], [0, 0], this.cursorColor, a, 1);
    this.set.push(c);
    this.set.push(a);
    this.vLine = c;
    this.hLine = a;
    this.hideCursor()
}, detectMovement: function () {
    var a = this.chart;
    if (a.mouseIsOver) {
        var b = a.mouseX - this.x, c = a.mouseY - this.y;
        0 < b && b < this.width && 0 < c && c < this.height ? (this.drawing ? this.rolledOver || a.setMouseCursor("crosshair") : this.pan && (this.rolledOver || a.setMouseCursor("move")), this.rolledOver = !0, this.setPosition()) : this.rolledOver && (this.handleMouseOut(),
            this.rolledOver = !1)
    } else this.rolledOver && (this.handleMouseOut(), this.rolledOver = !1)
}, getMousePosition: function () {
    var a, b = this.width, c = this.height;
    a = this.chart;
    this.rotate ? (a = a.mouseY - this.y, 0 > a && (a = 0), a > c && (a = c)) : (a = a.mouseX - this.x, 0 > a && (a = 0), a > b && (a = b));
    return a
}, updateCrosshair: function () {
    var a = this.chart, b = a.mouseX - this.x, c = a.mouseY - this.y, d = this.vLine, f = this.hLine, b = AmCharts.fitToBounds(b, 0, this.width), c = AmCharts.fitToBounds(c, 0, this.height);
    0 < this.cursorAlpha && (d.show(), f.show(), d.translate(b,
        0), f.translate(0, c));
    this.zooming && (a.hideXScrollbar && (b = NaN), a.hideYScrollbar && (c = NaN), this.updateSelectionSize(b, c));
    this.fireMoved();
    a.mouseIsOver || this.zooming || this.hideCursor()
}, fireMoved: function () {
    var a = this.chart, b = {type: "moved", target: this};
    b.chart = a;
    b.zooming = this.zooming;
    b.x = a.mouseX - this.x;
    b.y = a.mouseY - this.y;
    this.fire("moved", b)
}, updateSelectionSize: function (a, b) {
    AmCharts.remove(this.selection);
    var c = this.selectionPosX, d = this.selectionPosY, f = 0, e = 0, g = this.width, h = this.height;
    isNaN(a) ||
    (c > a && (f = a, g = c - a), c < a && (f = c, g = a - c), c == a && (f = a, g = 0));
    isNaN(b) || (d > b && (e = b, h = d - b), d < b && (e = d, h = b - d), d == b && (e = b, h = 0));
    0 < g && 0 < h && (c = AmCharts.rect(this.container, g, h, this.cursorColor, this.selectionAlpha), c.translate(f + this.x, e + this.y), this.selection = c)
}, arrangeBalloons: function () {
    var a = this.valueBalloons, b = this.x, c = this.y, d = this.height + c;
    a.sort(this.compareY);
    var f;
    for (f = 0; f < a.length; f++) {
        var e = a[f].balloon;
        e.setBounds(b, c, b + this.width, d);
        e.prevX = this.prevX[f];
        e.prevY = this.prevY[f];
        e.prevTX = this.prevTX[f];
        e.prevTY = this.prevTY[f];
        e.draw();
        d = e.yPos - 3
    }
    this.arrangeBalloons2()
}, compareY: function (a, b) {
    return a.yy < b.yy ? 1 : -1
}, arrangeBalloons2: function () {
    var a = this.valueBalloons;
    a.reverse();
    var b, c = this.x, d, f, e = a.length;
    for (f = 0; f < e; f++) {
        var g = a[f].balloon;
        b = g.bottom;
        var h = g.bottom - g.yPos, k = e - f - 1;
        0 < f && b - h < d + 3 && (g.setBounds(c, d + 3, c + this.width, d + h + 3), g.prevX = this.prevX[k], g.prevY = this.prevY[k], g.prevTX = this.prevTX[k], g.prevTY = this.prevTY[k], g.draw());
        g.set && g.set.show();
        this.prevX[k] = g.prevX;
        this.prevY[k] = g.prevY;
        this.prevTX[k] = g.prevTX;
        this.prevTY[k] = g.prevTY;
        d = g.bottom
    }
}, showBullets: function () {
    AmCharts.remove(this.allBullets);
    var a = this.container, b = a.set();
    this.set.push(b);
    this.set.show();
    this.allBullets = b;
    var b = this.chart.graphs, c;
    for (c = 0; c < b.length; c++) {
        var d = b[c];
        if (!d.hidden && d.balloonText) {
            var f = this.data[this.index].axes[d.valueAxis.id].graphs[d.id], e = f.y;
            if (!isNaN(e)) {
                var g, h;
                g = f.x;
                this.rotate ? (h = e, e = g) : h = g;
                d = AmCharts.circle(a, this.bulletSize / 2, this.chart.getBalloonColor(d, f, !0), d.cursorBulletAlpha);
                d.translate(h, e);
                this.allBullets.push(d)
            }
        }
    }
}, destroy: function () {
    this.clear();
    AmCharts.remove(this.selection);
    this.selection = null;
    var a = this.categoryBalloon;
    a && a.destroy();
    this.destroyValueBalloons();
    AmCharts.remove(this.set)
}, clear: function () {
    clearInterval(this.interval)
}, destroyValueBalloons: function () {
    var a = this.valueBalloons;
    if (a) {
        var b;
        for (b = 0; b < a.length; b++)a[b].balloon.hide()
    }
}, zoom: function (a, b, c, d) {
    var f = this.chart;
    this.destroyValueBalloons();
    this.zooming = !1;
    var e;
    this.rotate ? this.selectionPosY =
        e = f.mouseY : this.selectionPosX = e = f.mouseX;
    this.start = a;
    this.end = b;
    this.startTime = c;
    this.endTime = d;
    this.zoomed = !0;
    var g = f.categoryAxis, f = this.rotate;
    e = this.width;
    var h = this.height;
    g.parseDates && !g.equalSpacing ? (a = d - c + g.minDuration(), a = f ? h / a : e / a) : a = f ? h / (b - a) : e / (b - a);
    this.stepWidth = a;
    this.tempVal = this.valueBalloonsEnabled;
    this.valueBalloonsEnabled = !1;
    this.setPosition();
    this.valueBalloonsEnabled = this.tempVal;
    this.hideCursor()
}, hideObj: function (a) {
    a && a.hide()
}, hideCursor: function (a) {
    void 0 === a && (a = !0);
    this.hideObj(this.set);
    this.hideObj(this.categoryBalloon);
    this.hideObj(this.line);
    this.hideObj(this.vLine);
    this.hideObj(this.hLine);
    this.hideObj(this.allBullets);
    this.destroyValueBalloons();
    this.selectWithoutZooming || AmCharts.remove(this.selection);
    this.previousIndex = NaN;
    a && this.fire("onHideCursor", {type: "onHideCursor", chart: this.chart, target: this});
    this.drawing || this.chart.setMouseCursor("auto");
    this.normalizeBulletSize()
}, setPosition: function (a, b) {
    void 0 === b && (b = !0);
    if ("cursor" == this.type) {
        if (AmCharts.ifArray(this.data)) {
            isNaN(a) &&
            (a = this.getMousePosition());
            if ((a != this.previousMousePosition || !0 === this.zoomed || this.oneBalloonOnly) && !isNaN(a)) {
                var c = this.chart.categoryAxis.xToIndex(a);
                if (c != this.previousIndex || this.zoomed || "mouse" == this.cursorPosition || this.oneBalloonOnly)this.updateCursor(c, b), this.zoomed = !1
            }
            this.previousMousePosition = a
        }
    } else this.updateCrosshair()
}, normalizeBulletSize: function () {
    var a = this.resizedBullets;
    if (a)for (var b = 0; b < a.length; b++) {
        var c = a[b], d = c.bulletGraphics;
        d && d.translate(c.bx, c.by, 1)
    }
}, updateCursor: function (a, b) {
    var c = this.chart, d = c.mouseX - this.x, f = c.mouseY - this.y;
    this.drawingNow && (AmCharts.remove(this.drawingLine), this.drawingLine = AmCharts.line(this.container, [this.x + this.drawStartX, this.x + d], [this.y + this.drawStartY, this.y + f], this.cursorColor, 1, 1));
    if (this.enabled) {
        void 0 === b && (b = !0);
        this.index = a += this.adjustment;
        var e = c.categoryAxis, g = c.dx, h = c.dy, k = this.x, l = this.y, m = this.width, p = this.height, n = this.data[a];
        this.fireMoved();
        if (n) {
            var q = n.x[e.id], s = c.rotate, r = e.inside, u = this.stepWidth, v = this.categoryBalloon,
                t = this.firstTime, w = this.lastTime, z = this.cursorPosition, F = e.position, y = this.zooming, B = this.panning, G = c.graphs, K = e.axisThickness;
            if (c.mouseIsOver || y || B || this.forceShow)if (this.forceShow = !1, B) {
                var g = this.panClickPos, c = this.panClickEndTime, y = this.panClickStartTime, A = this.panClickEnd, k = this.panClickStart, d = (s ? g - f : g - d) / u;
                if (!e.parseDates || e.equalSpacing)d = Math.round(d);
                0 !== d && (g = {type: "zoomed", target: this}, g.chart = this.chart, e.parseDates && !e.equalSpacing ? (c + d > w && (d = w - c), y + d < t && (d = t - y), g.start = y + d, g.end =
                    c + d, this.fire(g.type, g)) : A + d >= this.data.length || 0 > k + d || (g.start = k + d, g.end = A + d, this.fire(g.type, g)))
            } else {
                "start" == z && (q -= e.cellWidth / 2);
                "mouse" == z && c.mouseIsOver && (q = s ? f - 2 : d - 2);
                if (s) {
                    if (0 > q)if (y)q = 0; else {
                        this.hideCursor();
                        return
                    }
                    if (q > p + 1)if (y)q = p + 1; else {
                        this.hideCursor();
                        return
                    }
                } else {
                    if (0 > q)if (y)q = 0; else {
                        this.hideCursor();
                        return
                    }
                    if (q > m)if (y)q = m; else {
                        this.hideCursor();
                        return
                    }
                }
                0 < this.cursorAlpha && (t = this.line, s ? (w = 0, u = q + h) : (w = q, u = 0), z = this.animationDuration, 0 < z && !this.zooming ? isNaN(this.previousX) ?
                    t.translate(w, u) : (t.translate(this.previousX, this.previousY), t.animate({translate: w + "," + u}, z, "easeOutSine")) : t.translate(w, u), this.previousX = w, this.previousY = u, t.show());
                this.linePos = s ? q + h : q;
                y && (s ? this.updateSelectionSize(NaN, q) : this.updateSelectionSize(q, NaN));
                u = !0;
                y && (u = !1);
                this.categoryBalloonEnabled && u ? (s ? (r && ("right" == F ? v.setBounds(k, l + h, k + m + g, l + q + h) : v.setBounds(k, l + h, k + m + g, l + q)), "right" == F ? r ? v.setPosition(k + m + g, l + q + h) : v.setPosition(k + m + g + K, l + q + h) : r ? v.setPosition(k, l + q) : v.setPosition(k - K, l + q)) :
                    "top" == F ? r ? v.setPosition(k + q + g, l + h) : v.setPosition(k + q + g, l + h - K + 1) : r ? v.setPosition(k + q, l + p) : v.setPosition(k + q, l + p + K - 1), (t = this.categoryBalloonFunction) ? v.showBalloon(t(n.category)) : e.parseDates ? (e = AmCharts.formatDate(n.category, this.categoryBalloonDateFormat), -1 != e.indexOf("fff") && (e = AmCharts.formatMilliseconds(e, n.category)), v.showBalloon(e)) : v.showBalloon(AmCharts.fixNewLines(n.category))) : v.hide();
                G && this.bulletsEnabled && this.showBullets();
                if (this.oneBalloonOnly) {
                    h = Infinity;
                    for (w = 0; w < G.length; w++)e =
                        G[w], e.showBalloon && !e.hidden && e.balloonText && (v = n.axes[e.valueAxis.id].graphs[e.id], t = v.y, isNaN(t) || (s ? Math.abs(d - t) < h && (h = Math.abs(d - t), A = e) : Math.abs(f - t) < h && (h = Math.abs(f - t), A = e)));
                    this.mostCloseGraph && (A = this.mostCloseGraph)
                }
                if (a != this.previousIndex || A != this.previousMostCloseGraph)if (this.normalizeBulletSize(), this.destroyValueBalloons(), this.resizedBullets = [], G && this.valueBalloonsEnabled && u && c.balloon.enabled) {
                    this.valueBalloons = h = [];
                    for (w = 0; w < G.length; w++)if (e = G[w], (!this.oneBalloonOnly || e ==
                        A) && e.showBalloon && !e.hidden && e.balloonText && ("step" == e.type && "left" == e.stepDirection && (n = this.data[a + 1]), n)) {
                        v = n.axes[e.valueAxis.id].graphs[e.id];
                        t = v.y;
                        if (this.showNextAvailable && isNaN(t) && a + 1 < this.data.length)for (q = a + 1; q < this.data.length; q++)if (r = this.data[q])if (v = r.axes[e.valueAxis.id].graphs[e.id], t = v.y, !isNaN(t))break;
                        if (!isNaN(t)) {
                            r = v.x;
                            u = !0;
                            if (s) {
                                if (q = t, 0 > r || r > p)u = !1
                            } else if (q = r, r = t, 0 > q || q > m + g + 1)u = !1;
                            u && (1 != this.graphBulletSize && AmCharts.isModern && (u = v.bulletGraphics) && (u.getBBox(), u.translate(v.bx,
                                v.by, this.graphBulletSize), this.resizedBullets.push(v)), u = e.valueBalloon, F = c.getBalloonColor(e, v), u.setBounds(k, l, k + m, l + p), u.pointerOrientation = "H", u.changeColor(F), void 0 !== e.balloonAlpha && (u.fillAlpha = e.balloonAlpha), void 0 !== e.balloonTextColor && (u.color = e.balloonTextColor), u.setPosition(q + k, r + l), q = c.formatString(e.balloonText, v, !0), (r = e.balloonFunction) && (q = r(v, e).toString()), "" !== q && (s ? u.showBalloon(q) : (u.text = q, u.show = !0)), !s && u.set && u.set.hide(), h.push({yy: t, balloon: u}))
                        }
                    }
                    s || this.arrangeBalloons()
                }
                b ?
                    (g = {type: "changed"}, g.index = a, g.chart = this.chart, g.zooming = y, g.mostCloseGraph = A, g.position = s ? f : d, g.target = this, c.fire("changed", g), this.fire("changed", g), this.skipZoomDispatch = !1) : (this.skipZoomDispatch = !0, c.updateLegendValues(a));
                this.previousIndex = a;
                this.previousMostCloseGraph = A
            }
        }
    } else this.hideCursor()
}, enableDrawing: function (a) {
    this.enabled = !a;
    this.hideCursor();
    this.rolledOver = !1;
    this.drawing = a
}, isZooming: function (a) {
    a && a != this.zooming && this.handleMouseDown("fake");
    a || a == this.zooming || this.handleMouseUp()
},
    handleMouseOut: function () {
        if (this.enabled)if (this.zooming)this.setPosition(); else {
            this.index = void 0;
            var a = {type: "changed", index: void 0, target: this};
            a.chart = this.chart;
            this.fire("changed", a);
            this.hideCursor()
        }
    }, handleReleaseOutside: function () {
        this.handleMouseUp()
    }, handleMouseUp: function () {
        var a = this.chart, b = this.data, c;
        if (a) {
            var d = a.mouseX - this.x, f = a.mouseY - this.y;
            if (this.drawingNow) {
                this.drawingNow = !1;
                AmCharts.remove(this.drawingLine);
                c = this.drawStartX;
                var e = this.drawStartY;
                if (2 < Math.abs(c - d) || 2 <
                    Math.abs(e - f))c = {type: "draw", target: this, chart: a, initialX: c, initialY: e, finalX: d, finalY: f}, this.fire(c.type, c)
            }
            if (this.enabled && 0 < b.length) {
                if (this.pan)this.rolledOver = !1; else if (this.zoomable && this.zooming) {
                    c = this.selectWithoutZooming ? {type: "selected"} : {type: "zoomed"};
                    c.target = this;
                    c.chart = a;
                    if ("cursor" == this.type)this.rotate ? this.selectionPosY = f : this.selectionPosX = f = d, 2 > Math.abs(f - this.initialMouse) && this.fromIndex == this.index || (this.index < this.fromIndex ? (c.end = this.fromIndex, c.start = this.index) :
                        (c.end = this.index, c.start = this.fromIndex), f = a.categoryAxis, f.parseDates && !f.equalSpacing && (c.start = b[c.start].time, c.end = a.getEndTime(b[c.end].time)), this.skipZoomDispatch || this.fire(c.type, c)); else {
                        var g = this.initialMouseX, h = this.initialMouseY;
                        3 > Math.abs(d - g) && 3 > Math.abs(f - h) || (b = Math.min(g, d), e = Math.min(h, f), d = Math.abs(g - d), f = Math.abs(h - f), a.hideXScrollbar && (b = 0, d = this.width), a.hideYScrollbar && (e = 0, f = this.height), c.selectionHeight = f, c.selectionWidth = d, c.selectionY = e, c.selectionX = b, this.skipZoomDispatch ||
                            this.fire(c.type, c))
                    }
                    this.selectWithoutZooming || AmCharts.remove(this.selection)
                }
                this.panning = this.zooming = this.skipZoomDispatch = !1
            }
        }
    }, showCursorAt: function (a) {
        var b = this.chart.categoryAxis;
        a = b.parseDates ? b.dateToCoordinate(a) : b.categoryToCoordinate(a);
        this.previousMousePosition = NaN;
        this.forceShow = !0;
        this.setPosition(a, !1)
    }, handleMouseDown: function (a) {
        if (this.zoomable || this.pan || this.drawing) {
            var b = this.rotate, c = this.chart, d = c.mouseX - this.x, f = c.mouseY - this.y;
            if (0 < d && d < this.width && 0 < f && f < this.height ||
                "fake" == a)this.setPosition(), this.selectWithoutZooming && AmCharts.remove(this.selection), this.drawing ? (this.drawStartY = f, this.drawStartX = d, this.drawingNow = !0) : this.pan ? (this.zoomable = !1, c.setMouseCursor("move"), this.panning = !0, this.panClickPos = b ? f : d, this.panClickStart = this.start, this.panClickEnd = this.end, this.panClickStartTime = this.startTime, this.panClickEndTime = this.endTime) : this.zoomable && ("cursor" == this.type ? (this.fromIndex = this.index, b ? (this.initialMouse = f, this.selectionPosY = this.linePos) : (this.initialMouse =
                d, this.selectionPosX = this.linePos)) : (this.initialMouseX = d, this.initialMouseY = f, this.selectionPosX = d, this.selectionPosY = f), this.zooming = !0)
        }
    }});
AmCharts.SimpleChartScrollbar = AmCharts.Class({construct: function (a) {
    this.createEvents("zoomed");
    this.backgroundColor = "#D4D4D4";
    this.backgroundAlpha = 1;
    this.selectedBackgroundColor = "#EFEFEF";
    this.scrollDuration = this.selectedBackgroundAlpha = 1;
    this.resizeEnabled = !0;
    this.hideResizeGrips = !1;
    this.scrollbarHeight = 20;
    this.updateOnReleaseOnly = !1;
    9 > document.documentMode && (this.updateOnReleaseOnly = !0);
    this.dragIconWidth = 18;
    this.dragIconHeight = 25;
    AmCharts.applyTheme(this, a, "SimpleChartScrollbar")
}, draw: function () {
    var a =
        this;
    a.destroy();
    a.interval = setInterval(function () {
        a.updateScrollbar.call(a)
    }, 40);
    var b = a.chart.container, c = a.rotate, d = a.chart, f = b.set();
    a.set = f;
    d.scrollbarsSet.push(f);
    var e, g;
    c ? (e = a.scrollbarHeight, g = d.plotAreaHeight) : (g = a.scrollbarHeight, e = d.plotAreaWidth);
    a.width = e;
    if ((a.height = g) && e) {
        var h = AmCharts.rect(b, e, g, a.backgroundColor, a.backgroundAlpha, 1, a.backgroundColor, a.backgroundAlpha);
        a.bg = h;
        f.push(h);
        h = AmCharts.rect(b, e, g, "#000", 0.005);
        f.push(h);
        a.invisibleBg = h;
        h.click(function () {
            a.handleBgClick()
        }).mouseover(function () {
            a.handleMouseOver()
        }).mouseout(function () {
            a.handleMouseOut()
        }).touchend(function () {
            a.handleBgClick()
        });
        h = AmCharts.rect(b, e, g, a.selectedBackgroundColor, a.selectedBackgroundAlpha);
        a.selectedBG = h;
        f.push(h);
        e = AmCharts.rect(b, e, g, "#000", 0.005);
        a.dragger = e;
        f.push(e);
        e.mousedown(function (b) {
            a.handleDragStart(b)
        }).mouseup(function () {
            a.handleDragStop()
        }).mouseover(function () {
            a.handleDraggerOver()
        }).mouseout(function () {
            a.handleMouseOut()
        }).touchstart(function (b) {
            a.handleDragStart(b)
        }).touchend(function () {
            a.handleDragStop()
        });
        e = d.pathToImages;
        c ? (h = e + "dragIconH.gif", e = a.dragIconWidth, c = a.dragIconHeight) : (h = e +
            "dragIcon.gif", c = a.dragIconWidth, e = a.dragIconHeight);
        g = b.image(h, 0, 0, c, e);
        var h = b.image(h, 0, 0, c, e), k = 10, l = 20;
        d.panEventsEnabled && (k = 25, l = a.scrollbarHeight);
        var m = AmCharts.rect(b, k, l, "#000", 0.005), p = AmCharts.rect(b, k, l, "#000", 0.005);
        p.translate(-(k - c) / 2, -(l - e) / 2);
        m.translate(-(k - c) / 2, -(l - e) / 2);
        c = b.set([g, p]);
        b = b.set([h, m]);
        a.iconLeft = c;
        a.iconRight = b;
        c.mousedown(function () {
            a.leftDragStart()
        }).mouseup(function () {
            a.leftDragStop()
        }).mouseover(function () {
            a.iconRollOver()
        }).mouseout(function () {
            a.iconRollOut()
        }).touchstart(function (b) {
            a.leftDragStart()
        }).touchend(function () {
            a.leftDragStop()
        });
        b.mousedown(function () {
            a.rightDragStart()
        }).mouseup(function () {
            a.rightDragStop()
        }).mouseover(function () {
            a.iconRollOver()
        }).mouseout(function () {
            a.iconRollOut()
        }).touchstart(function (b) {
            a.rightDragStart()
        }).touchend(function () {
            a.rightDragStop()
        });
        AmCharts.ifArray(d.chartData) ? f.show() : f.hide();
        a.hideDragIcons();
        a.clipDragger(!1)
    }
    f.translate(a.x, a.y)
}, updateScrollbarSize: function (a, b) {
    var c = this.dragger, d, f, e, g;
    this.rotate ? (d = 0, f = a, e = this.width + 1, g = b - a, c.setAttr("height", b - a), c.setAttr("y", f)) : (d = a,
        f = 0, e = b - a, g = this.height + 1, c.setAttr("width", b - a), c.setAttr("x", d));
    this.clipAndUpdate(d, f, e, g)
}, updateScrollbar: function () {
    var a, b = !1, c, d, f = this.x, e = this.y, g = this.dragger, h = this.getDBox();
    c = h.x + f;
    d = h.y + e;
    var k = h.width, h = h.height, l = this.rotate, m = this.chart, p = this.width, n = this.height, q = m.mouseX, s = m.mouseY;
    a = this.initialMouse;
    m.mouseIsOver && (this.dragging && (m = this.initialCoord, l ? (a = m + (s - a), 0 > a && (a = 0), m = n - h, a > m && (a = m), g.setAttr("y", a)) : (a = m + (q - a), 0 > a && (a = 0), m = p - k, a > m && (a = m), g.setAttr("x", a))), this.resizingRight &&
        (l ? (a = s - d, a + d > n + e && (a = n - d + e), 0 > a ? (this.resizingRight = !1, b = this.resizingLeft = !0) : (0 === a && (a = 0.1), g.setAttr("height", a))) : (a = q - c, a + c > p + f && (a = p - c + f), 0 > a ? (this.resizingRight = !1, b = this.resizingLeft = !0) : (0 === a && (a = 0.1), g.setAttr("width", a)))), this.resizingLeft && (l ? (c = d, d = s, d < e && (d = e), d > n + e && (d = n + e), a = !0 === b ? c - d : h + c - d, 0 > a ? (this.resizingRight = !0, this.resizingLeft = !1, g.setAttr("y", c + h - e)) : (0 === a && (a = 0.1), g.setAttr("y", d - e), g.setAttr("height", a))) : (d = q, d < f && (d = f), d > p + f && (d = p + f), a = !0 === b ? c - d : k + c - d, 0 > a ? (this.resizingRight = !0, this.resizingLeft = !1, g.setAttr("x", c + k - f)) : (0 === a && (a = 0.1), g.setAttr("x", d - f), g.setAttr("width", a)))), this.clipDragger(!0))
}, clipDragger: function (a) {
    var b = this.getDBox();
    if (b) {
        var c = b.x, d = b.y, f = b.width, b = b.height, e = !1;
        if (this.rotate) {
            if (c = 0, f = this.width + 1, this.clipY != d || this.clipH != b)e = !0
        } else if (d = 0, b = this.height + 1, this.clipX != c || this.clipW != f)e = !0;
        e && (this.clipAndUpdate(c, d, f, b), a && (this.updateOnReleaseOnly || this.dispatchScrollbarEvent()))
    }
}, maskGraphs: function () {
}, clipAndUpdate: function (a, b, c, d) {
    this.clipX = a;
    this.clipY = b;
    this.clipW = c;
    this.clipH = d;
    this.selectedBG.clipRect(a, b, c, d);
    this.updateDragIconPositions();
    this.maskGraphs(a, b, c, d)
}, dispatchScrollbarEvent: function () {
    if (this.skipEvent)this.skipEvent = !1; else {
        var a = this.chart;
        a.hideBalloon();
        var b = this.getDBox(), c = b.x, d = b.y, f = b.width, b = b.height;
        this.rotate ? (c = d, f = this.height / b) : f = this.width / f;
        a = {type: "zoomed", position: c, chart: a, target: this, multiplier: f};
        this.fire(a.type, a)
    }
}, updateDragIconPositions: function () {
    var a = this.getDBox(), b =
        a.x, c = a.y, d = this.iconLeft, f = this.iconRight, e, g, h = this.scrollbarHeight;
    this.rotate ? (e = this.dragIconWidth, g = this.dragIconHeight, d.translate(this.x + (h - g) / 2, this.y + c - e / 2), f.translate(this.x + (h - g) / 2, this.y + c + a.height - e / 2)) : (e = this.dragIconHeight, g = this.dragIconWidth, d.translate(this.x + b - g / 2, this.y + (h - e) / 2), f.translate(this.x + b - g / 2 + a.width, this.y + (h - e) / 2))
}, showDragIcons: function () {
    this.resizeEnabled && (this.iconLeft.show(), this.iconRight.show())
}, hideDragIcons: function () {
    this.resizingLeft || this.resizingRight ||
        this.dragging || (this.hideResizeGrips && (this.iconLeft.hide(), this.iconRight.hide()), this.removeCursors())
}, removeCursors: function () {
    this.chart.setMouseCursor("auto")
}, relativeZoom: function (a, b) {
    this.dragger.stop();
    this.multiplier = a;
    this.position = b;
    this.updateScrollbarSize(b, this.rotate ? b + this.height / a : b + this.width / a)
}, destroy: function () {
    this.clear();
    AmCharts.remove(this.set);
    AmCharts.remove(this.iconRight);
    AmCharts.remove(this.iconLeft)
}, clear: function () {
    clearInterval(this.interval)
}, handleDragStart: function () {
    var a =
        this.chart;
    this.dragger.stop();
    this.removeCursors();
    this.dragging = !0;
    var b = this.getDBox();
    this.rotate ? (this.initialCoord = b.y, this.initialMouse = a.mouseY) : (this.initialCoord = b.x, this.initialMouse = a.mouseX)
}, handleDragStop: function () {
    this.updateOnReleaseOnly && (this.updateScrollbar(), this.skipEvent = !1, this.dispatchScrollbarEvent());
    this.dragging = !1;
    this.mouseIsOver && this.removeCursors();
    this.updateScrollbar()
}, handleDraggerOver: function () {
    this.handleMouseOver()
}, leftDragStart: function () {
    this.dragger.stop();
    this.resizingLeft = !0
}, leftDragStop: function () {
    this.resizingLeft = !1;
    this.mouseIsOver || this.removeCursors();
    this.updateOnRelease()
}, rightDragStart: function () {
    this.dragger.stop();
    this.resizingRight = !0
}, rightDragStop: function () {
    this.resizingRight = !1;
    this.mouseIsOver || this.removeCursors();
    this.updateOnRelease()
}, iconRollOut: function () {
    this.removeCursors()
}, iconRollOver: function () {
    this.rotate ? this.chart.setMouseCursor("n-resize") : this.chart.setMouseCursor("e-resize");
    this.handleMouseOver()
}, getDBox: function () {
    if (this.dragger)return this.dragger.getBBox()
},
    handleBgClick: function () {
        if (!this.resizingRight && !this.resizingLeft) {
            this.zooming = !0;
            var a, b, c = this.scrollDuration, d = this.dragger;
            a = this.getDBox();
            var f = a.height, e = a.width;
            b = this.chart;
            var g = this.y, h = this.x, k = this.rotate;
            k ? (a = "y", b = b.mouseY - f / 2 - g, b = AmCharts.fitToBounds(b, 0, this.height - f)) : (a = "x", b = b.mouseX - e / 2 - h, b = AmCharts.fitToBounds(b, 0, this.width - e));
            this.updateOnReleaseOnly ? (this.skipEvent = !1, d.setAttr(a, b), this.dispatchScrollbarEvent(), this.clipDragger()) : (b = Math.round(b), k ? d.animate({y: b}, c,
                ">") : d.animate({x: b}, c, ">"))
        }
    }, updateOnRelease: function () {
        this.updateOnReleaseOnly && (this.updateScrollbar(), this.skipEvent = !1, this.dispatchScrollbarEvent())
    }, handleReleaseOutside: function () {
        if (this.set) {
            if (this.resizingLeft || this.resizingRight || this.dragging)this.updateOnRelease(), this.removeCursors();
            this.mouseIsOver = this.dragging = this.resizingRight = this.resizingLeft = !1;
            this.hideDragIcons();
            this.updateScrollbar()
        }
    }, handleMouseOver: function () {
        this.mouseIsOver = !0;
        this.showDragIcons()
    }, handleMouseOut: function () {
        this.mouseIsOver = !1;
        this.hideDragIcons()
    }});
AmCharts.ChartScrollbar = AmCharts.Class({inherits: AmCharts.SimpleChartScrollbar, construct: function (a) {
    this.cname = "ChartScrollbar";
    AmCharts.ChartScrollbar.base.construct.call(this, a);
    this.graphLineColor = "#BBBBBB";
    this.graphLineAlpha = 0;
    this.graphFillColor = "#BBBBBB";
    this.graphFillAlpha = 1;
    this.selectedGraphLineColor = "#888888";
    this.selectedGraphLineAlpha = 0;
    this.selectedGraphFillColor = "#888888";
    this.selectedGraphFillAlpha = 1;
    this.gridCount = 0;
    this.gridColor = "#FFFFFF";
    this.gridAlpha = 0.7;
    this.skipEvent = this.autoGridCount = !1;
    this.color = "#FFFFFF";
    this.scrollbarCreated = !1;
    this.offset = 0;
    AmCharts.applyTheme(this, a, this.cname)
}, init: function () {
    var a = this.categoryAxis, b = this.chart;
    a || (this.categoryAxis = a = new AmCharts.CategoryAxis);
    a.chart = b;
    a.id = "scrollbar";
    a.dateFormats = b.categoryAxis.dateFormats;
    a.markPeriodChange = b.categoryAxis.markPeriodChange;
    a.boldPeriodBeginning = b.categoryAxis.boldPeriodBeginning;
    a.axisItemRenderer = AmCharts.RecItem;
    a.axisRenderer = AmCharts.RecAxis;
    a.guideFillRenderer = AmCharts.RecFill;
    a.inside = !0;
    a.fontSize =
        this.fontSize;
    a.tickLength = 0;
    a.axisAlpha = 0;
    AmCharts.isString(this.graph) && (this.graph = AmCharts.getObjById(b.graphs, this.graph));
    if (a = this.graph) {
        var c = this.valueAxis;
        c || (this.valueAxis = c = new AmCharts.ValueAxis, c.visible = !1, c.scrollbar = !0, c.axisItemRenderer = AmCharts.RecItem, c.axisRenderer = AmCharts.RecAxis, c.guideFillRenderer = AmCharts.RecFill, c.labelsEnabled = !1, c.chart = b);
        b = this.unselectedGraph;
        b || (b = new AmCharts.AmGraph, b.scrollbar = !0, this.unselectedGraph = b, b.negativeBase = a.negativeBase, b.noStepRisers =
            a.noStepRisers);
        b = this.selectedGraph;
        b || (b = new AmCharts.AmGraph, b.scrollbar = !0, this.selectedGraph = b, b.negativeBase = a.negativeBase, b.noStepRisers = a.noStepRisers)
    }
    this.scrollbarCreated = !0
}, draw: function () {
    var a = this;
    AmCharts.ChartScrollbar.base.draw.call(a);
    a.scrollbarCreated || a.init();
    var b = a.chart, c = b.chartData, d = a.categoryAxis, f = a.rotate, e = a.x, g = a.y, h = a.width, k = a.height, l = b.categoryAxis, m = a.set;
    d.setOrientation(!f);
    d.parseDates = l.parseDates;
    d.rotate = f;
    d.equalSpacing = l.equalSpacing;
    d.minPeriod = l.minPeriod;
    d.startOnAxis = l.startOnAxis;
    d.viW = h;
    d.viH = k;
    d.width = h;
    d.height = k;
    d.gridCount = a.gridCount;
    d.gridColor = a.gridColor;
    d.gridAlpha = a.gridAlpha;
    d.color = a.color;
    d.tickLength = 0;
    d.axisAlpha = 0;
    d.autoGridCount = a.autoGridCount;
    d.parseDates && !d.equalSpacing && d.timeZoom(b.firstTime, b.lastTime);
    d.zoom(0, c.length - 1);
    if (l = a.graph) {
        var p = a.valueAxis, n = l.valueAxis;
        p.id = n.id;
        p.rotate = f;
        p.setOrientation(f);
        p.width = h;
        p.height = k;
        p.viW = h;
        p.viH = k;
        p.dataProvider = c;
        p.reversed = n.reversed;
        p.logarithmic = n.logarithmic;
        p.gridAlpha =
            0;
        p.axisAlpha = 0;
        m.push(p.set);
        f ? (p.y = g, p.x = 0) : (p.x = e, p.y = 0);
        var e = Infinity, g = -Infinity, q;
        for (q = 0; q < c.length; q++) {
            var s = c[q].axes[n.id].graphs[l.id].values, r;
            for (r in s)if (s.hasOwnProperty(r) && "percents" != r && "total" != r) {
                var u = s[r];
                u < e && (e = u);
                u > g && (g = u)
            }
        }
        Infinity != e && (p.minimum = e);
        -Infinity != g && (p.maximum = g + 0.1 * (g - e));
        e == g && (p.minimum -= 1, p.maximum += 1);
        void 0 !== a.minimum && (p.minimum = a.minimum);
        void 0 !== a.maximum && (p.maximum = a.maximum);
        p.zoom(0, c.length - 1);
        r = a.unselectedGraph;
        r.id = l.id;
        r.rotate = f;
        r.chart =
            b;
        r.data = c;
        r.valueAxis = p;
        r.chart = l.chart;
        r.categoryAxis = a.categoryAxis;
        r.periodSpan = l.periodSpan;
        r.valueField = l.valueField;
        r.openField = l.openField;
        r.closeField = l.closeField;
        r.highField = l.highField;
        r.lowField = l.lowField;
        r.lineAlpha = a.graphLineAlpha;
        r.lineColorR = a.graphLineColor;
        r.fillAlphas = a.graphFillAlpha;
        r.fillColorsR = a.graphFillColor;
        r.connect = l.connect;
        r.hidden = l.hidden;
        r.width = h;
        r.height = k;
        r.pointPosition = l.pointPosition;
        r.stepDirection = l.stepDirection;
        r.periodSpan = l.periodSpan;
        n = a.selectedGraph;
        n.id = l.id;
        n.rotate = f;
        n.chart = b;
        n.data = c;
        n.valueAxis = p;
        n.chart = l.chart;
        n.categoryAxis = d;
        n.periodSpan = l.periodSpan;
        n.valueField = l.valueField;
        n.openField = l.openField;
        n.closeField = l.closeField;
        n.highField = l.highField;
        n.lowField = l.lowField;
        n.lineAlpha = a.selectedGraphLineAlpha;
        n.lineColorR = a.selectedGraphLineColor;
        n.fillAlphas = a.selectedGraphFillAlpha;
        n.fillColorsR = a.selectedGraphFillColor;
        n.connect = l.connect;
        n.hidden = l.hidden;
        n.width = h;
        n.height = k;
        n.pointPosition = l.pointPosition;
        n.stepDirection = l.stepDirection;
        n.periodSpan = l.periodSpan;
        b = a.graphType;
        b || (b = l.type);
        r.type = b;
        n.type = b;
        c = c.length - 1;
        r.zoom(0, c);
        n.zoom(0, c);
        n.set.click(function () {
            a.handleBackgroundClick()
        }).mouseover(function () {
            a.handleMouseOver()
        }).mouseout(function () {
            a.handleMouseOut()
        });
        r.set.click(function () {
            a.handleBackgroundClick()
        }).mouseover(function () {
            a.handleMouseOver()
        }).mouseout(function () {
            a.handleMouseOut()
        });
        m.push(r.set);
        m.push(n.set)
    }
    m.push(d.set);
    m.push(d.labelsSet);
    a.bg.toBack();
    a.invisibleBg.toFront();
    a.dragger.toFront();
    a.iconLeft.toFront();
    a.iconRight.toFront()
}, timeZoom: function (a, b, c) {
    this.startTime = a;
    this.endTime = b;
    this.timeDifference = b - a;
    this.skipEvent = !AmCharts.toBoolean(c);
    this.zoomScrollbar();
    this.skipEvent || this.dispatchScrollbarEvent()
}, zoom: function (a, b) {
    this.start = a;
    this.end = b;
    this.skipEvent = !0;
    this.zoomScrollbar()
}, dispatchScrollbarEvent: function () {
    if (this.skipEvent)this.skipEvent = !1; else {
        var a = this.chart.chartData, b, c, d = this.dragger.getBBox();
        b = d.x;
        c = d.y;
        var f = d.width, e = d.height, d = this.chart;
        this.rotate ? (b = c, c = e) : c = f;
        f =
        {type: "zoomed", target: this};
        f.chart = d;
        var e = this.categoryAxis, g = this.stepWidth;
        if (e.parseDates && !e.equalSpacing) {
            if (a = d.firstTime, e.minDuration(), d = Math.round(b / g) + a, a = this.dragging ? d + this.timeDifference : Math.round((b + c) / g) + a, d > a && (d = a), d != this.startTime || a != this.endTime)this.startTime = d, this.endTime = a, f.start = d, f.end = a, f.startDate = new Date(d), f.endDate = new Date(a), this.fire(f.type, f)
        } else if (e.startOnAxis || (b += g / 2), c -= this.stepWidth / 2, d = e.xToIndex(b), b = e.xToIndex(b + c), d != this.start || this.end != b)e.startOnAxis &&
            (this.resizingRight && d == b && b++, this.resizingLeft && d == b && (0 < d ? d-- : b = 1)), this.start = d, this.end = this.dragging ? this.start + this.difference : b, f.start = this.start, f.end = this.end, e.parseDates && (a[this.start] && (f.startDate = new Date(a[this.start].time)), a[this.end] && (f.endDate = new Date(a[this.end].time))), this.fire(f.type, f)
    }
}, zoomScrollbar: function () {
    var a, b;
    a = this.chart;
    var c = a.chartData, d = this.categoryAxis;
    d.parseDates && !d.equalSpacing ? (c = d.stepWidth, d = a.firstTime, a = c * (this.startTime - d), b = c * (this.endTime -
        d)) : (a = c[this.start].x[d.id], b = c[this.end].x[d.id], c = d.stepWidth, d.startOnAxis || (d = c / 2, a -= d, b += d));
    this.stepWidth = c;
    this.updateScrollbarSize(a, b)
}, maskGraphs: function (a, b, c, d) {
    var f = this.selectedGraph;
    f && f.set.clipRect(a, b, c, d)
}, handleDragStart: function () {
    AmCharts.ChartScrollbar.base.handleDragStart.call(this);
    this.difference = this.end - this.start;
    this.timeDifference = this.endTime - this.startTime;
    0 > this.timeDifference && (this.timeDifference = 0)
}, handleBackgroundClick: function () {
    AmCharts.ChartScrollbar.base.handleBackgroundClick.call(this);
    this.dragging || (this.difference = this.end - this.start, this.timeDifference = this.endTime - this.startTime, 0 > this.timeDifference && (this.timeDifference = 0))
}});
AmCharts.AmBalloon = AmCharts.Class({construct: function (a) {
    this.cname = "AmBalloon";
    this.enabled = !0;
    this.fillColor = "#FFFFFF";
    this.fillAlpha = 0.8;
    this.borderThickness = 2;
    this.borderColor = "#FFFFFF";
    this.borderAlpha = 1;
    this.cornerRadius = 0;
    this.maximumWidth = 220;
    this.horizontalPadding = 8;
    this.verticalPadding = 4;
    this.pointerWidth = 6;
    this.pointerOrientation = "V";
    this.color = "#000000";
    this.adjustBorderColor = !0;
    this.show = this.follow = this.showBullet = !1;
    this.bulletSize = 3;
    this.shadowAlpha = 0.4;
    this.shadowColor = "#000000";
    this.fadeOutDuration = this.animationDuration = 0.3;
    this.fixedPosition = !1;
    this.offsetY = 6;
    this.offsetX = 1;
    AmCharts.isModern || (this.offsetY *= 1.5);
    AmCharts.applyTheme(this, a, this.cname)
}, draw: function () {
    var a = this.pointToX, b = this.pointToY;
    this.deltaSignX = this.deltaSignY = 1;
    var c = this.chart;
    AmCharts.VML && (this.fadeOutDuration = 0);
    this.xAnim && c.stopAnim(this.xAnim);
    this.yAnim && c.stopAnim(this.yAnim);
    if (!isNaN(a)) {
        var d = this.follow, f = c.container, e = this.set;
        AmCharts.remove(e);
        this.removeDiv();
        this.set = e = f.set();
        c.balloonsSet.push(e);
        if (this.show) {
            var g = this.l, h = this.t, k = this.r, l = this.b, m = this.balloonColor, p = this.fillColor, n = this.borderColor, q = p;
            void 0 != m && (this.adjustBorderColor ? q = n = m : p = m);
            var s = this.horizontalPadding, r = this.verticalPadding, u = this.pointerWidth, v = this.pointerOrientation, t = this.cornerRadius, w = c.fontFamily, z = this.fontSize;
            void 0 == z && (z = c.fontSize);
            var m = document.createElement("div"), F = m.style;
            F.position = "absolute";
            m.innerHTML = '<div style="max-width:' + this.maxWidth + "px; font-size:" + z + "px; color:" +
                this.color + "; font-family:" + w + '">' + this.text + "</div>";
            c.chartDiv.appendChild(m);
            this.textDiv = m;
            z = m.offsetWidth;
            w = m.offsetHeight;
            m.clientHeight && (z = m.clientWidth, w = m.clientHeight);
            var w = w + 2 * r, y = z + 2 * s;
            window.opera && (w += 2);
            var B, G = !1;
            B = this.offsetY;
            c.handDrawn && (B += c.handDrawScatter + 2);
            "H" != v ? (z = a - y / 2, b < h + w + 10 && "down" != v ? (G = !0, d && (b += B), B = b + u, this.deltaSignY = -1) : (d && (b -= B), B = b - w - u, this.deltaSignY = 1)) : (2 * u > w && (u = w / 2), B = b - w / 2, a < g + (k - g) / 2 ? (z = a + u, this.deltaSignX = -1) : (z = a - y - u, this.deltaSignX = 1));
            B + w >= l &&
            (B = l - w);
            B < h && (B = h);
            z < g && (z = g);
            z + y > k && (z = k - y);
            var h = B + r, l = z + s, r = this.shadowAlpha, K = this.shadowColor, s = this.borderThickness, A = this.bulletSize, S;
            0 < t || 0 === u ? (0 < r && (a = AmCharts.rect(f, y, w, p, 0, s + 1, K, r, this.cornerRadius), AmCharts.isModern ? a.translate(1, 1) : a.translate(4, 4), e.push(a)), p = AmCharts.rect(f, y, w, p, this.fillAlpha, s, n, this.borderAlpha, this.cornerRadius), this.showBullet && (S = AmCharts.circle(f, A, q, this.fillAlpha), e.push(S))) : (q = [], t = [], "H" != v ? (g = a - z, g > y - u && (g = y - u), g < u && (g = u), q = [0, g - u, a - z, g + u, y, y, 0, 0],
                t = G ? [0, 0, b - B, 0, 0, w, w, 0] : [w, w, b - B, w, w, 0, 0, w]) : (q = b - B, q > w - u && (q = w - u), q < u && (q = u), t = [0, q - u, b - B, q + u, w, w, 0, 0], q = a < g + (k - g) / 2 ? [0, 0, z < a ? 0 : a - z, 0, 0, y, y, 0] : [y, y, z + y > a ? y : a - z, y, y, 0, 0, y]), 0 < r && (a = AmCharts.polygon(f, q, t, p, 0, s, K, r), a.translate(1, 1), e.push(a)), p = AmCharts.polygon(f, q, t, p, this.fillAlpha, s, n, this.borderAlpha));
            this.bg = p;
            e.push(p);
            p.toFront();
            f = 1 * this.deltaSignX;
            F.left = l + "px";
            F.top = h + "px";
            e.translate(z - f, B);
            p = p.getBBox();
            this.bottom = B + w + 1;
            this.yPos = p.y + B;
            S && S.translate(this.pointToX - z + f, b - B);
            b = this.animationDuration;
            0 < this.animationDuration && !d && !isNaN(this.prevX) && (e.translate(this.prevX, this.prevY), e.animate({translate: z - f + "," + B}, b, "easeOutSine"), m && (F.left = this.prevTX + "px", F.top = this.prevTY + "px", this.xAnim = c.animate({node: m}, "left", this.prevTX, l, b, "easeOutSine", "px"), this.yAnim = c.animate({node: m}, "top", this.prevTY, h, b, "easeOutSine", "px")));
            this.prevX = z - f;
            this.prevY = B;
            this.prevTX = l;
            this.prevTY = h
        }
    }
}, followMouse: function () {
    if (this.follow && this.show) {
        var a = this.chart.mouseX - this.offsetX * this.deltaSignX, b = this.chart.mouseY;
        this.pointToX = a;
        this.pointToY = b;
        if (a != this.previousX || b != this.previousY)if (this.previousX = a, this.previousY = b, 0 === this.cornerRadius)this.draw(); else {
            var c = this.set;
            if (c) {
                var d = c.getBBox(), a = a - d.width / 2, f = b - d.height - 10;
                a < this.l && (a = this.l);
                a > this.r - d.width && (a = this.r - d.width);
                f < this.t && (f = b + 10);
                c.translate(a, f);
                b = this.textDiv.style;
                b.left = a + this.horizontalPadding + "px";
                b.top = f + this.verticalPadding + "px"
            }
        }
    }
}, changeColor: function (a) {
    this.balloonColor = a
}, setBounds: function (a, b, c, d) {
    this.l = a;
    this.t = b;
    this.r =
        c;
    this.b = d;
    this.destroyTO && clearTimeout(this.destroyTO)
}, showBalloon: function (a) {
    this.text = a;
    this.show = !0;
    this.destroyTO && clearTimeout(this.destroyTO);
    a = this.chart;
    this.fadeAnim1 && a.stopAnim(this.fadeAnim1);
    this.fadeAnim2 && a.stopAnim(this.fadeAnim2);
    this.draw()
}, hide: function () {
    var a = this, b = a.fadeOutDuration, c = a.chart;
    if (0 < b) {
        a.destroyTO = setTimeout(function () {
            a.destroy.call(a)
        }, 1E3 * b);
        a.follow = !1;
        a.show = !1;
        var d = a.set;
        d && (d.setAttr("opacity", a.fillAlpha), a.fadeAnim1 = d.animate({opacity: 0}, b, "easeInSine"));
        a.textDiv && (a.fadeAnim2 = c.animate({node: a.textDiv}, "opacity", 1, 0, b, "easeInSine", ""))
    } else a.show = !1, a.follow = !1, a.destroy()
}, setPosition: function (a, b, c) {
    this.pointToX = a;
    this.pointToY = b;
    c && (a == this.previousX && b == this.previousY || this.draw());
    this.previousX = a;
    this.previousY = b
}, followCursor: function (a) {
    var b = this;
    (b.follow = a) ? (b.pShowBullet = b.showBullet, b.showBullet = !1) : void 0 !== b.pShowBullet && (b.showBullet = b.pShowBullet);
    clearInterval(b.interval);
    var c = b.chart.mouseX, d = b.chart.mouseY;
    !isNaN(c) && a && (b.pointToX =
        c - b.offsetX * b.deltaSignX, b.pointToY = d, b.followMouse(), b.interval = setInterval(function () {
        b.followMouse.call(b)
    }, 40))
}, removeDiv: function () {
    if (this.textDiv) {
        var a = this.textDiv.parentNode;
        a && a.removeChild(this.textDiv)
    }
}, destroy: function () {
    clearInterval(this.interval);
    AmCharts.remove(this.set);
    this.removeDiv();
    this.set = null
}});
AmCharts.AmCoordinateChart = AmCharts.Class({inherits: AmCharts.AmChart, construct: function (a) {
    AmCharts.AmCoordinateChart.base.construct.call(this, a);
    this.theme = a;
    this.createEvents("rollOverGraphItem", "rollOutGraphItem", "clickGraphItem", "doubleClickGraphItem", "rightClickGraphItem", "clickGraph", "rollOverGraph", "rollOutGraph");
    this.startAlpha = 1;
    this.startDuration = 0;
    this.startEffect = "elastic";
    this.sequencedAnimation = !0;
    this.colors = "#FF6600 #FCD202 #B0DE09 #0D8ECF #2A0CD0 #CD0D74 #CC0000 #00CC00 #0000CC #DDDDDD #999999 #333333 #990000".split(" ");
    this.balloonDateFormat = "MMM DD, YYYY";
    this.valueAxes = [];
    this.graphs = [];
    this.gridAboveGraphs = !1;
    AmCharts.applyTheme(this, a, "AmCoordinateChart")
}, initChart: function () {
    AmCharts.AmCoordinateChart.base.initChart.call(this);
    var a = this.categoryAxis;
    a && (this.categoryAxis = AmCharts.processObject(a, AmCharts.CategoryAxis, this.theme));
    this.processValueAxes();
    this.createValueAxes();
    this.processGraphs();
    AmCharts.VML && (this.startAlpha = 1);
    this.setLegendData(this.graphs);
    this.gridAboveGraphs && this.gridSet.toFront()
},
    createValueAxes: function () {
        if (0 === this.valueAxes.length) {
            var a = new AmCharts.ValueAxis;
            this.addValueAxis(a)
        }
    }, parseData: function () {
        this.processValueAxes();
        this.processGraphs()
    }, parseSerialData: function () {
        var a = this.graphs, b, c = {}, d = this.seriesIdField;
        d || (d = this.categoryField);
        this.chartData = [];
        var f = this.dataProvider;
        if (f) {
            var e = !1, g, h = this.categoryAxis, k;
            h && (e = h.parseDates, k = h.forceShowField, g = h.categoryFunction);
            var l, m;
            e && (b = AmCharts.extractPeriod(h.minPeriod), l = b.period, m = b.count);
            var p = {};
            this.lookupTable =
                p;
            var n, q = this.dataDateFormat;
            for (n = 0; n < f.length; n++) {
                var s = {}, r = f[n];
                b = r[this.categoryField];
                s.dataContext = r;
                s.category = g ? g(b, r, h) : String(b);
                k && (s.forceShow = r[k]);
                p[r[d]] = s;
                e && (b = h.categoryFunction ? h.categoryFunction(b, r, h) : b instanceof Date ? "fff" == h.minPeriod ? AmCharts.useUTC ? new Date(b.getUTCFullYear(), b.getUTCMonth(), b.getUTCDate(), b.getUTCHours(), b.getUTCMinutes(), b.getUTCSeconds(), b.getUTCMilliseconds()) : new Date(b.getFullYear(), b.getMonth(), b.getDate(), b.getHours(), b.getMinutes(), b.getSeconds(),
                    b.getMilliseconds()) : new Date(b) : q ? AmCharts.stringToDate(b, q) : new Date(b), b = AmCharts.resetDateToMin(b, l, m, h.firstDayOfWeek), s.category = b, s.time = b.getTime());
                var u = this.valueAxes;
                s.axes = {};
                s.x = {};
                var v;
                for (v = 0; v < u.length; v++) {
                    var t = u[v].id;
                    s.axes[t] = {};
                    s.axes[t].graphs = {};
                    var w;
                    for (w = 0; w < a.length; w++) {
                        b = a[w];
                        var z = b.id, F = b.periodValue;
                        if (b.valueAxis.id == t) {
                            s.axes[t].graphs[z] = {};
                            var y = {};
                            y.index = n;
                            var B = r;
                            b.dataProvider && (B = c);
                            y.values = this.processValues(B, b, F);
                            this.processFields(b, y, B);
                            y.category =
                                s.category;
                            y.serialDataItem = s;
                            y.graph = b;
                            s.axes[t].graphs[z] = y
                        }
                    }
                }
                this.chartData[n] = s
            }
        }
        for (c = 0; c < a.length; c++)b = a[c], b.dataProvider && this.parseGraphData(b)
    }, processValues: function (a, b, c) {
        var d = {}, f, e = !1;
        "candlestick" != b.type && "ohlc" != b.type || "" === c || (e = !0);
        f = Number(a[b.valueField + c]);
        isNaN(f) || (d.value = f);
        f = Number(a[b.errorField + c]);
        isNaN(f) || (d.error = f);
        e && (c = "Open");
        f = Number(a[b.openField + c]);
        isNaN(f) || (d.open = f);
        e && (c = "Close");
        f = Number(a[b.closeField + c]);
        isNaN(f) || (d.close = f);
        e && (c = "Low");
        f = Number(a[b.lowField +
            c]);
        isNaN(f) || (d.low = f);
        e && (c = "High");
        f = Number(a[b.highField + c]);
        isNaN(f) || (d.high = f);
        return d
    }, parseGraphData: function (a) {
        var b = a.dataProvider, c = a.seriesIdField;
        c || (c = this.seriesIdField);
        c || (c = this.categoryField);
        var d;
        for (d = 0; d < b.length; d++) {
            var f = b[d], e = this.lookupTable[String(f[c])], g = a.valueAxis.id;
            e && (g = e.axes[g].graphs[a.id], g.serialDataItem = e, g.values = this.processValues(f, a, a.periodValue), this.processFields(a, g, f))
        }
    }, addValueAxis: function (a) {
        a.chart = this;
        this.valueAxes.push(a);
        this.validateData()
    },
    removeValueAxesAndGraphs: function () {
        var a = this.valueAxes, b;
        for (b = a.length - 1; -1 < b; b--)this.removeValueAxis(a[b])
    }, removeValueAxis: function (a) {
        var b = this.graphs, c;
        for (c = b.length - 1; 0 <= c; c--) {
            var d = b[c];
            d && d.valueAxis == a && this.removeGraph(d)
        }
        b = this.valueAxes;
        for (c = b.length - 1; 0 <= c; c--)b[c] == a && b.splice(c, 1);
        this.validateData()
    }, addGraph: function (a) {
        this.graphs.push(a);
        this.chooseGraphColor(a, this.graphs.length - 1);
        this.validateData()
    }, removeGraph: function (a) {
        var b = this.graphs, c;
        for (c = b.length - 1; 0 <= c; c--)b[c] ==
            a && (b.splice(c, 1), a.destroy());
        this.validateData()
    }, processValueAxes: function () {
        var a = this.valueAxes, b;
        for (b = 0; b < a.length; b++) {
            var c = a[b], c = AmCharts.processObject(c, AmCharts.ValueAxis, this.theme);
            a[b] = c;
            c.chart = this;
            c.id || (c.id = "valueAxisAuto" + b + "_" + (new Date).getTime());
            void 0 === c.usePrefixes && (c.usePrefixes = this.usePrefixes)
        }
    }, processGraphs: function () {
        var a = this.graphs, b;
        for (b = 0; b < a.length; b++) {
            var c = a[b], c = AmCharts.processObject(c, AmCharts.AmGraph, this.theme);
            a[b] = c;
            this.chooseGraphColor(c, b);
            c.chart = this;
            AmCharts.isString(c.valueAxis) && (c.valueAxis = this.getValueAxisById(c.valueAxis));
            c.valueAxis || (c.valueAxis = this.valueAxes[0]);
            c.id || (c.id = "graphAuto" + b + "_" + (new Date).getTime())
        }
    }, formatString: function (a, b, c) {
        var d = b.graph, f = d.valueAxis;
        f.duration && b.values.value && (f = AmCharts.formatDuration(b.values.value, f.duration, "", f.durationUnits, f.maxInterval, f.numberFormatter), a = a.split("[[value]]").join(f));
        a = AmCharts.massReplace(a, {"[[title]]": d.title, "[[description]]": b.description});
        a = c ? AmCharts.fixNewLines(a) :
            AmCharts.fixBrakes(a);
        return a = AmCharts.cleanFromEmpty(a)
    }, getBalloonColor: function (a, b, c) {
        var d = a.lineColor, f = a.balloonColor;
        c && (f = d);
        c = a.fillColorsR;
        "object" == typeof c ? d = c[0] : void 0 !== c && (d = c);
        b.isNegative && (c = a.negativeLineColor, a = a.negativeFillColors, "object" == typeof a ? c = a[0] : void 0 !== a && (c = a), void 0 !== c && (d = c));
        void 0 !== b.color && (d = b.color);
        void 0 === f && (f = d);
        return f
    }, getGraphById: function (a) {
        return AmCharts.getObjById(this.graphs, a)
    }, getValueAxisById: function (a) {
        return AmCharts.getObjById(this.valueAxes,
            a)
    }, processFields: function (a, b, c) {
        if (a.itemColors) {
            var d = a.itemColors, f = b.index;
            b.color = f < d.length ? d[f] : AmCharts.randomColor()
        }
        d = "lineColor color alpha fillColors description bullet customBullet bulletSize bulletConfig url labelColor dashLength pattern".split(" ");
        for (f = 0; f < d.length; f++) {
            var e = d[f], g = a[e + "Field"];
            g && (g = c[g], AmCharts.isDefined(g) && (b[e] = g))
        }
        b.dataContext = c
    }, chooseGraphColor: function (a, b) {
        if (a.lineColor)a.lineColorR = a.lineColor; else {
            var c;
            c = this.colors.length > b ? this.colors[b] : AmCharts.randomColor();
            a.lineColorR = c
        }
        a.fillColorsR = a.fillColors ? a.fillColors : a.lineColorR;
        a.bulletBorderColorR = a.bulletBorderColor ? a.bulletBorderColor : a.useLineColorForBulletBorder ? a.lineColorR : a.bulletColor;
        a.bulletColorR = a.bulletColor ? a.bulletColor : a.lineColorR;
        if (c = this.patterns)a.pattern = c[b]
    }, handleLegendEvent: function (a) {
        var b = a.type;
        a = a.dataItem;
        if (!this.legend.data && a) {
            var c = a.hidden, d = a.showBalloon;
            switch (b) {
                case "clickMarker":
                    d ? this.hideGraphsBalloon(a) : this.showGraphsBalloon(a);
                    break;
                case "clickLabel":
                    d ? this.hideGraphsBalloon(a) :
                        this.showGraphsBalloon(a);
                    break;
                case "rollOverItem":
                    c || this.highlightGraph(a);
                    break;
                case "rollOutItem":
                    c || this.unhighlightGraph();
                    break;
                case "hideItem":
                    this.hideGraph(a);
                    break;
                case "showItem":
                    this.showGraph(a)
            }
        }
    }, highlightGraph: function (a) {
        var b = this.graphs, c, d = 0.2;
        this.legend && (d = this.legend.rollOverGraphAlpha);
        if (1 != d)for (c = 0; c < b.length; c++) {
            var f = b[c];
            f != a && f.changeOpacity(d)
        }
    }, unhighlightGraph: function () {
        var a;
        this.legend && (a = this.legend.rollOverGraphAlpha);
        if (1 != a) {
            a = this.graphs;
            var b;
            for (b =
                     0; b < a.length; b++)a[b].changeOpacity(1)
        }
    }, showGraph: function (a) {
        a.hidden = !1;
        this.dataChanged = !0;
        this.marginsUpdated = !1;
        this.chartCreated && this.initChart()
    }, hideGraph: function (a) {
        this.dataChanged = !0;
        this.marginsUpdated = !1;
        a.hidden = !0;
        this.chartCreated && this.initChart()
    }, hideGraphsBalloon: function (a) {
        a.showBalloon = !1;
        this.updateLegend()
    }, showGraphsBalloon: function (a) {
        a.showBalloon = !0;
        this.updateLegend()
    }, updateLegend: function () {
        this.legend && this.legend.invalidateSize()
    }, resetAnimation: function () {
        var a =
            this.graphs;
        if (a) {
            var b;
            for (b = 0; b < a.length; b++)a[b].animationPlayed = !1
        }
    }, animateAgain: function () {
        this.resetAnimation();
        this.validateNow()
    }});
AmCharts.AmSlicedChart = AmCharts.Class({inherits: AmCharts.AmChart, construct: function (a) {
    this.createEvents("rollOverSlice", "rollOutSlice", "clickSlice", "pullOutSlice", "pullInSlice", "rightClickSlice");
    AmCharts.AmSlicedChart.base.construct.call(this, a);
    this.colors = "#FF0F00 #FF6600 #FF9E01 #FCD202 #F8FF01 #B0DE09 #04D215 #0D8ECF #0D52D1 #2A0CD0 #8A0CCF #CD0D74 #754DEB #DDDDDD #999999 #333333 #000000 #57032A #CA9726 #990000 #4B0C25".split(" ");
    this.alpha = 1;
    this.groupPercent = 0;
    this.groupedTitle = "Other";
    this.groupedPulled = !1;
    this.groupedAlpha = 1;
    this.marginLeft = 0;
    this.marginBottom = this.marginTop = 10;
    this.marginRight = 0;
    this.hoverAlpha = 1;
    this.outlineColor = "#FFFFFF";
    this.outlineAlpha = 0;
    this.outlineThickness = 1;
    this.startAlpha = 0;
    this.startDuration = 1;
    this.startEffect = "bounce";
    this.sequencedAnimation = !0;
    this.pullOutDuration = 1;
    this.pullOutEffect = "bounce";
    this.pullOnHover = this.pullOutOnlyOne = !1;
    this.labelsEnabled = !0;
    this.labelTickColor = "#000000";
    this.labelTickAlpha = 0.2;
    this.hideLabelsPercent = 0;
    this.urlTarget = "_self";
    this.autoMarginOffset =
        10;
    this.gradientRatio = [];
    AmCharts.applyTheme(this, a, "AmSlicedChart")
}, initChart: function () {
    AmCharts.AmSlicedChart.base.initChart.call(this);
    this.dataChanged && (this.parseData(), this.dispatchDataUpdated = !0, this.dataChanged = !1, this.setLegendData(this.chartData));
    this.drawChart()
}, handleLegendEvent: function (a) {
    var b = a.type;
    a = a.dataItem;
    if (!this.legend.data && a) {
        var c = a.hidden;
        switch (b) {
            case "clickMarker":
                c || this.clickSlice(a);
                break;
            case "clickLabel":
                c || this.clickSlice(a);
                break;
            case "rollOverItem":
                c || this.rollOverSlice(a,
                    !1);
                break;
            case "rollOutItem":
                c || this.rollOutSlice(a);
                break;
            case "hideItem":
                this.hideSlice(a);
                break;
            case "showItem":
                this.showSlice(a)
        }
    }
}, invalidateVisibility: function () {
    this.recalculatePercents();
    this.initChart();
    var a = this.legend;
    a && a.invalidateSize()
}, addEventListeners: function (a, b) {
    var c = this;
    a.mouseover(function (a) {
        c.rollOverSlice(b, !0, a)
    }).mouseout(function (a) {
        c.rollOutSlice(b, a)
    }).touchend(function (a) {
        c.rollOverSlice(b, a);
        c.panEventsEnabled && c.clickSlice(b, a)
    }).touchstart(function (a) {
        c.rollOverSlice(b,
            a)
    }).click(function (a) {
        c.clickSlice(b, a)
    }).contextmenu(function (a) {
        c.handleRightClick(b, a)
    })
}, formatString: function (a, b, c) {
    a = AmCharts.formatValue(a, b, ["value"], this.numberFormatter, "", this.usePrefixes, this.prefixesOfSmallNumbers, this.prefixesOfBigNumbers);
    a = AmCharts.formatValue(a, b, ["percents"], this.percentFormatter);
    a = AmCharts.massReplace(a, {"[[title]]": b.title, "[[description]]": b.description});
    -1 != a.indexOf("[[") && (a = AmCharts.formatDataContextValue(a, b.dataContext));
    a = c ? AmCharts.fixNewLines(a) :
        AmCharts.fixBrakes(a);
    return a = AmCharts.cleanFromEmpty(a)
}, startSlices: function () {
    var a;
    for (a = 0; a < this.chartData.length; a++)0 < this.startDuration && this.sequencedAnimation ? this.setStartTO(a) : this.startSlice(this.chartData[a])
}, setStartTO: function (a) {
    var b = this;
    a = setTimeout(function () {
        b.startSequenced.call(b)
    }, b.startDuration / b.chartData.length * 500 * a);
    b.timeOuts.push(a)
}, pullSlices: function (a) {
    var b = this.chartData, c;
    for (c = 0; c < b.length; c++) {
        var d = b[c];
        d.pulled && this.pullSlice(d, 1, a)
    }
}, startSequenced: function () {
    var a =
        this.chartData, b;
    for (b = 0; b < a.length; b++)if (!a[b].started) {
        this.startSlice(this.chartData[b]);
        break
    }
}, startSlice: function (a) {
    a.started = !0;
    var b = a.wedge, c = this.startDuration;
    b && 0 < c && (0 < a.alpha && b.show(), b.translate(a.startX, a.startY), b.animate({opacity: 1, translate: "0,0"}, c, this.startEffect))
}, showLabels: function () {
    var a = this.chartData, b;
    for (b = 0; b < a.length; b++) {
        var c = a[b];
        if (0 < c.alpha) {
            var d = c.label;
            d && d.show();
            (c = c.tick) && c.show()
        }
    }
}, showSlice: function (a) {
    isNaN(a) ? a.hidden = !1 : this.chartData[a].hidden = !1;
    this.invalidateVisibility()
}, hideSlice: function (a) {
    isNaN(a) ? a.hidden = !0 : this.chartData[a].hidden = !0;
    this.hideBalloon();
    this.invalidateVisibility()
}, rollOverSlice: function (a, b, c) {
    isNaN(a) || (a = this.chartData[a]);
    clearTimeout(this.hoverInt);
    if (!a.hidden) {
        this.pullOnHover && this.pullSlice(a, 1);
        1 > this.hoverAlpha && a.wedge && a.wedge.attr({opacity: this.hoverAlpha});
        var d = a.balloonX, f = a.balloonY;
        a.pulled && (d += a.pullX, f += a.pullY);
        var e = this.formatString(this.balloonText, a, !0), g = AmCharts.adjustLuminosity(a.color,
            -0.15);
        this.showBalloon(e, g, b, d, f);
        a = {type: "rollOverSlice", dataItem: a, chart: this, event: c};
        this.fire(a.type, a)
    }
}, rollOutSlice: function (a, b) {
    isNaN(a) || (a = this.chartData[a]);
    a.wedge && a.wedge.attr({opacity: 1});
    this.hideBalloon();
    var c = {type: "rollOutSlice", dataItem: a, chart: this, event: b};
    this.fire(c.type, c)
}, clickSlice: function (a, b) {
    isNaN(a) || (a = this.chartData[a]);
    a.pulled ? this.pullSlice(a, 0) : this.pullSlice(a, 1);
    AmCharts.getURL(a.url, this.urlTarget);
    var c = {type: "clickSlice", dataItem: a, chart: this, event: b};
    this.fire(c.type, c)
}, handleRightClick: function (a, b) {
    isNaN(a) || (a = this.chartData[a]);
    var c = {type: "rightClickSlice", dataItem: a, chart: this, event: b};
    this.fire(c.type, c)
}, drawTicks: function () {
    var a = this.chartData, b;
    for (b = 0; b < a.length; b++) {
        var c = a[b];
        if (c.label) {
            var d = c.ty, d = AmCharts.line(this.container, [c.tx0, c.tx, c.tx2], [c.ty0, d, d], this.labelTickColor, this.labelTickAlpha);
            c.tick = d;
            c.wedge.push(d)
        }
    }
}, initialStart: function () {
    var a = this, b = a.startDuration, c = setTimeout(function () {
        a.showLabels.call(a)
    }, 1E3 *
        b);
    a.timeOuts.push(c);
    a.chartCreated ? a.pullSlices(!0) : (b = setTimeout(function () {
        a.pullSlices.call(a)
    }, 1200 * b), a.timeOuts.push(b), a.startSlices())
}, pullSlice: function (a, b, c) {
    var d = this.pullOutDuration;
    !0 === c && (d = 0);
    (c = a.wedge) && c.animate({translate: b * a.pullX + "," + b * a.pullY}, d, this.pullOutEffect);
    1 == b ? (a.pulled = !0, this.pullOutOnlyOne && this.pullInAll(a.index), a = {type: "pullOutSlice", dataItem: a, chart: this}) : (a.pulled = !1, a = {type: "pullInSlice", dataItem: a, chart: this});
    this.fire(a.type, a)
}, pullInAll: function (a) {
    var b =
        this.chartData, c;
    for (c = 0; c < this.chartData.length; c++)c != a && b[c].pulled && this.pullSlice(b[c], 0)
}, pullOutAll: function (a) {
    a = this.chartData;
    var b;
    for (b = 0; b < a.length; b++)a[b].pulled || this.pullSlice(a[b], 1)
}, parseData: function () {
    var a = [];
    this.chartData = a;
    var b = this.dataProvider;
    isNaN(this.pieAlpha) || (this.alpha = this.pieAlpha);
    if (void 0 !== b) {
        var c = b.length, d = 0, f, e, g;
        for (f = 0; f < c; f++) {
            e = {};
            var h = b[f];
            e.dataContext = h;
            e.value = Number(h[this.valueField]);
            (g = h[this.titleField]) || (g = "");
            e.title = g;
            e.pulled = AmCharts.toBoolean(h[this.pulledField],
                !1);
            (g = h[this.descriptionField]) || (g = "");
            e.description = g;
            e.labelRadius = Number(h[this.labelRadiusField]);
            e.url = h[this.urlField];
            g = h[this.patternField];
            !g && this.patterns && (g = this.patterns[f]);
            e.pattern = g;
            e.visibleInLegend = AmCharts.toBoolean(h[this.visibleInLegendField], !0);
            g = h[this.alphaField];
            e.alpha = void 0 !== g ? Number(g) : this.alpha;
            g = h[this.colorField];
            void 0 !== g && (e.color = AmCharts.toColor(g));
            e.labelColor = AmCharts.toColor(h[this.labelColorField]);
            d += e.value;
            e.hidden = !1;
            a[f] = e
        }
        for (f = b = 0; f < c; f++)e =
            a[f], e.percents = e.value / d * 100, e.percents < this.groupPercent && b++;
        1 < b && (this.groupValue = 0, this.removeSmallSlices(), a.push({title: this.groupedTitle, value: this.groupValue, percents: this.groupValue / d * 100, pulled: this.groupedPulled, color: this.groupedColor, url: this.groupedUrl, description: this.groupedDescription, alpha: this.groupedAlpha, pattern: this.groupedPattern}));
        c = this.baseColor;
        c || (c = this.pieBaseColor);
        d = this.brightnessStep;
        d || (d = this.pieBrightnessStep);
        for (f = 0; f < a.length; f++)c ? g = AmCharts.adjustLuminosity(c,
            f * d / 100) : (g = this.colors[f], void 0 === g && (g = AmCharts.randomColor())), void 0 === a[f].color && (a[f].color = g);
        this.recalculatePercents()
    }
}, recalculatePercents: function () {
    var a = this.chartData, b = 0, c, d;
    for (c = 0; c < a.length; c++)d = a[c], !d.hidden && 0 < d.value && (b += d.value);
    for (c = 0; c < a.length; c++)d = this.chartData[c], d.percents = !d.hidden && 0 < d.value ? 100 * d.value / b : 0
}, removeSmallSlices: function () {
    var a = this.chartData, b;
    for (b = a.length - 1; 0 <= b; b--)a[b].percents < this.groupPercent && (this.groupValue += a[b].value, a.splice(b, 1))
},
    animateAgain: function () {
        var a = this;
        a.startSlices();
        var b = setTimeout(function () {
            a.pullSlices.call(a)
        }, 1200 * a.startDuration);
        a.timeOuts.push(b)
    }, measureMaxLabel: function () {
        var a = this.chartData, b = 0, c;
        for (c = 0; c < a.length; c++) {
            var d = this.formatString(this.labelText, a[c]), d = AmCharts.text(this.container, d, this.color, this.fontFamily, this.fontSize), f = d.getBBox().width;
            f > b && (b = f);
            d.remove()
        }
        return b
    }});
AmCharts.AmRectangularChart = AmCharts.Class({inherits: AmCharts.AmCoordinateChart, construct: function (a) {
    AmCharts.AmRectangularChart.base.construct.call(this, a);
    this.theme = a;
    this.createEvents("zoomed");
    this.marginRight = this.marginBottom = this.marginTop = this.marginLeft = 20;
    this.verticalPosition = this.horizontalPosition = this.depth3D = this.angle = 0;
    this.heightMultiplier = this.widthMultiplier = 1;
    this.plotAreaFillColors = "#FFFFFF";
    this.plotAreaFillAlphas = 0;
    this.plotAreaBorderColor = "#000000";
    this.plotAreaBorderAlpha =
        0;
    this.zoomOutButtonImageSize = 17;
    this.zoomOutButtonImage = "lens.png";
    this.zoomOutText = "Show all";
    this.zoomOutButtonColor = "#e5e5e5";
    this.zoomOutButtonAlpha = 0;
    this.zoomOutButtonRollOverAlpha = 1;
    this.zoomOutButtonPadding = 8;
    this.trendLines = [];
    this.autoMargins = !0;
    this.marginsUpdated = !1;
    this.autoMarginOffset = 10;
    AmCharts.applyTheme(this, a, "AmRectangularChart")
}, initChart: function () {
    AmCharts.AmRectangularChart.base.initChart.call(this);
    this.updateDxy();
    var a = !0;
    !this.marginsUpdated && this.autoMargins && (this.resetMargins(),
        a = !1);
    this.processScrollbars();
    this.updateMargins();
    this.updatePlotArea();
    this.updateScrollbars();
    this.updateTrendLines();
    this.updateChartCursor();
    this.updateValueAxes();
    a && (this.scrollbarOnly || this.updateGraphs())
}, drawChart: function () {
    AmCharts.AmRectangularChart.base.drawChart.call(this);
    this.drawPlotArea();
    if (AmCharts.ifArray(this.chartData)) {
        var a = this.chartCursor;
        a && a.draw();
        a = this.zoomOutText;
        "" !== a && a && this.drawZoomOutButton()
    }
}, resetMargins: function () {
    var a = {}, b;
    if ("serial" == this.type) {
        var c =
            this.valueAxes;
        for (b = 0; b < c.length; b++) {
            var d = c[b];
            d.ignoreAxisWidth || (d.setOrientation(this.rotate), d.fixAxisPosition(), a[d.position] = !0)
        }
        (b = this.categoryAxis) && !b.ignoreAxisWidth && (b.setOrientation(!this.rotate), b.fixAxisPosition(), b.fixAxisPosition(), a[b.position] = !0)
    } else {
        d = this.xAxes;
        c = this.yAxes;
        for (b = 0; b < d.length; b++) {
            var f = d[b];
            f.ignoreAxisWidth || (f.setOrientation(!0), f.fixAxisPosition(), a[f.position] = !0)
        }
        for (b = 0; b < c.length; b++)d = c[b], d.ignoreAxisWidth || (d.setOrientation(!1), d.fixAxisPosition(),
            a[d.position] = !0)
    }
    a.left && (this.marginLeft = 0);
    a.right && (this.marginRight = 0);
    a.top && (this.marginTop = 0);
    a.bottom && (this.marginBottom = 0);
    this.fixMargins = a
}, measureMargins: function () {
    var a = this.valueAxes, b, c = this.autoMarginOffset, d = this.fixMargins, f = this.realWidth, e = this.realHeight, g = c, h = c, k = f;
    b = e;
    var l;
    for (l = 0; l < a.length; l++)b = this.getAxisBounds(a[l], g, k, h, b), g = b.l, k = b.r, h = b.t, b = b.b;
    if (a = this.categoryAxis)b = this.getAxisBounds(a, g, k, h, b), g = b.l, k = b.r, h = b.t, b = b.b;
    d.left && g < c && (this.marginLeft = Math.round(-g +
        c));
    d.right && k >= f - c && (this.marginRight = Math.round(k - f + c));
    d.top && h < c + this.titleHeight && (this.marginTop = Math.round(this.marginTop - h + c + this.titleHeight));
    d.bottom && b > e - c && (this.marginBottom = Math.round(this.marginBottom + b - e + c));
    this.initChart()
}, getAxisBounds: function (a, b, c, d, f) {
    if (!a.ignoreAxisWidth) {
        var e = a.labelsSet, g = a.tickLength;
        a.inside && (g = 0);
        if (e)switch (e = a.getBBox(), a.position) {
            case "top":
                a = e.y;
                d > a && (d = a);
                break;
            case "bottom":
                a = e.y + e.height;
                f < a && (f = a);
                break;
            case "right":
                a = e.x + e.width + g + 3;
                c < a &&
                (c = a);
                break;
            case "left":
                a = e.x - g, b > a && (b = a)
        }
    }
    return{l: b, t: d, r: c, b: f}
}, drawZoomOutButton: function () {
    var a = this, b = a.container.set();
    a.zoomButtonSet.push(b);
    var c = a.color, d = a.fontSize, f = a.zoomOutButtonImageSize, e = a.zoomOutButtonImage, g = a.zoomOutText, h = a.zoomOutButtonColor, k = a.zoomOutButtonAlpha, l = a.zoomOutButtonFontSize, m = a.zoomOutButtonPadding;
    isNaN(l) || (d = l);
    (l = a.zoomOutButtonFontColor) && (c = l);
    var l = a.zoomOutButton, p;
    l && (l.fontSize && (d = l.fontSize), l.color && (c = l.color), l.backgroundColor && (h = l.backgroundColor),
        isNaN(l.backgroundAlpha) || (a.zoomOutButtonRollOverAlpha = l.backgroundAlpha));
    var n = l = 0;
    void 0 !== a.pathToImages && e && (p = a.container.image(a.pathToImages + e, 0, 0, f, f), b.push(p), p = p.getBBox(), l = p.width + 5);
    void 0 !== g && (c = AmCharts.text(a.container, g, c, a.fontFamily, d, "start"), d = c.getBBox(), n = p ? p.height / 2 - 3 : d.height / 2, c.translate(l, n), b.push(c));
    p = b.getBBox();
    c = 1;
    AmCharts.isModern || (c = 0);
    h = AmCharts.rect(a.container, p.width + 2 * m + 5, p.height + 2 * m - 2, h, 1, 1, h, c);
    h.setAttr("opacity", k);
    h.translate(-m, -m);
    b.push(h);
    h.toBack();
    a.zbBG = h;
    p = h.getBBox();
    b.translate(a.marginLeftReal + a.plotAreaWidth - p.width + m, a.marginTopReal + m);
    b.hide();
    b.mouseover(function () {
        a.rollOverZB()
    }).mouseout(function () {
        a.rollOutZB()
    }).click(function () {
        a.clickZB()
    }).touchstart(function () {
        a.rollOverZB()
    }).touchend(function () {
        a.rollOutZB();
        a.clickZB()
    });
    for (k = 0; k < b.length; k++)b[k].attr({cursor: "pointer"});
    a.zbSet = b
}, rollOverZB: function () {
    this.zbBG.setAttr("opacity", this.zoomOutButtonRollOverAlpha)
}, rollOutZB: function () {
    this.zbBG.setAttr("opacity", this.zoomOutButtonAlpha)
},
    clickZB: function () {
        this.zoomOut()
    }, zoomOut: function () {
        this.updateScrollbar = !0;
        this.zoom()
    }, drawPlotArea: function () {
        var a = this.dx, b = this.dy, c = this.marginLeftReal, d = this.marginTopReal, f = this.plotAreaWidth - 1, e = this.plotAreaHeight - 1, g = this.plotAreaFillColors, h = this.plotAreaFillAlphas, k = this.plotAreaBorderColor, l = this.plotAreaBorderAlpha;
        this.trendLinesSet.clipRect(c, d, f, e);
        "object" == typeof h && (h = h[0]);
        g = AmCharts.polygon(this.container, [0, f, f, 0, 0], [0, 0, e, e, 0], g, h, 1, k, l, this.plotAreaGradientAngle);
        g.translate(c +
            a, d + b);
        this.set.push(g);
        0 !== a && 0 !== b && (g = this.plotAreaFillColors, "object" == typeof g && (g = g[0]), g = AmCharts.adjustLuminosity(g, -0.15), f = AmCharts.polygon(this.container, [0, a, f + a, f, 0], [0, b, b, 0, 0], g, h, 1, k, l), f.translate(c, d + e), this.set.push(f), a = AmCharts.polygon(this.container, [0, 0, a, a, 0], [0, e, e + b, b, 0], g, h, 1, k, l), a.translate(c, d), this.set.push(a));
        (c = this.bbset) && this.scrollbarOnly && c.remove()
    }, updatePlotArea: function () {
        var a = this.updateWidth(), b = this.updateHeight(), c = this.container;
        this.realWidth = a;
        this.realWidth =
            b;
        c && this.container.setSize(a, b);
        a = a - this.marginLeftReal - this.marginRightReal - this.dx;
        b = b - this.marginTopReal - this.marginBottomReal;
        1 > a && (a = 1);
        1 > b && (b = 1);
        this.plotAreaWidth = Math.round(a);
        this.plotAreaHeight = Math.round(b)
    }, updateDxy: function () {
        this.dx = Math.round(this.depth3D * Math.cos(this.angle * Math.PI / 180));
        this.dy = Math.round(-this.depth3D * Math.sin(this.angle * Math.PI / 180));
        this.d3x = Math.round(this.columnSpacing3D * Math.cos(this.angle * Math.PI / 180));
        this.d3y = Math.round(-this.columnSpacing3D * Math.sin(this.angle *
            Math.PI / 180))
    }, updateMargins: function () {
        var a = this.getTitleHeight();
        this.titleHeight = a;
        this.marginTopReal = this.marginTop - this.dy + a;
        this.marginBottomReal = this.marginBottom;
        this.marginLeftReal = this.marginLeft;
        this.marginRightReal = this.marginRight
    }, updateValueAxes: function () {
        var a = this.valueAxes, b = this.marginLeftReal, c = this.marginTopReal, d = this.plotAreaHeight, f = this.plotAreaWidth, e;
        for (e = 0; e < a.length; e++) {
            var g = a[e];
            g.axisRenderer = AmCharts.RecAxis;
            g.guideFillRenderer = AmCharts.RecFill;
            g.axisItemRenderer =
                AmCharts.RecItem;
            g.dx = this.dx;
            g.dy = this.dy;
            g.viW = f - 1;
            g.viH = d - 1;
            g.marginsChanged = !0;
            g.viX = b;
            g.viY = c;
            this.updateObjectSize(g)
        }
    }, updateObjectSize: function (a) {
        a.width = (this.plotAreaWidth - 1) * this.widthMultiplier;
        a.height = (this.plotAreaHeight - 1) * this.heightMultiplier;
        a.x = this.marginLeftReal + this.horizontalPosition;
        a.y = this.marginTopReal + this.verticalPosition
    }, updateGraphs: function () {
        var a = this.graphs, b;
        for (b = 0; b < a.length; b++) {
            var c = a[b];
            c.x = this.marginLeftReal + this.horizontalPosition;
            c.y = this.marginTopReal +
                this.verticalPosition;
            c.width = this.plotAreaWidth * this.widthMultiplier;
            c.height = this.plotAreaHeight * this.heightMultiplier;
            c.index = b;
            c.dx = this.dx;
            c.dy = this.dy;
            c.rotate = this.rotate
        }
    }, updateChartCursor: function () {
        var a = this.chartCursor;
        a && (a = AmCharts.processObject(a, AmCharts.ChartCursor, this.theme), this.addChartCursor(a), a.x = this.marginLeftReal, a.y = this.marginTopReal, a.width = this.plotAreaWidth - 1, a.height = this.plotAreaHeight - 1, a.chart = this)
    }, processScrollbars: function () {
        var a = this.chartScrollbar;
        a && (a =
            AmCharts.processObject(a, AmCharts.ChartScrollbar, this.theme), this.addChartScrollbar(a))
    }, updateScrollbars: function () {
    }, addChartCursor: function (a) {
        AmCharts.callMethod("destroy", [this.chartCursor]);
        a && (this.listenTo(a, "changed", this.handleCursorChange), this.listenTo(a, "zoomed", this.handleCursorZoom));
        this.chartCursor = a
    }, removeChartCursor: function () {
        AmCharts.callMethod("destroy", [this.chartCursor]);
        this.chartCursor = null
    }, zoomTrendLines: function () {
        var a = this.trendLines, b;
        for (b = 0; b < a.length; b++) {
            var c =
                a[b];
            c.valueAxis.recalculateToPercents ? c.set && c.set.hide() : (c.x = this.marginLeftReal + this.horizontalPosition, c.y = this.marginTopReal + this.verticalPosition, c.draw())
        }
    }, addTrendLine: function (a) {
        this.trendLines.push(a)
    }, removeTrendLine: function (a) {
        var b = this.trendLines, c;
        for (c = b.length - 1; 0 <= c; c--)b[c] == a && b.splice(c, 1)
    }, adjustMargins: function (a, b) {
        var c = a.scrollbarHeight + a.offset;
        "top" == a.position ? b ? this.marginLeftReal += c : this.marginTopReal += c : b ? this.marginRightReal += c : this.marginBottomReal += c
    }, getScrollbarPosition: function (a, b, c) {
        a.position = b ? "bottom" == c || "left" == c ? "bottom" : "top" : "top" == c || "right" == c ? "bottom" : "top"
    }, updateChartScrollbar: function (a, b) {
        if (a) {
            a.rotate = b;
            var c = this.marginTopReal, d = this.marginLeftReal, f = a.scrollbarHeight, e = this.dx, g = this.dy, h = a.offset;
            "top" == a.position ? b ? (a.y = c, a.x = d - f - h) : (a.y = c - f + g - 1 - h, a.x = d + e) : b ? (a.y = c + g, a.x = d + this.plotAreaWidth + e + h) : (a.y = c + this.plotAreaHeight + h, a.x = this.marginLeftReal)
        }
    }, showZB: function (a) {
        var b = this.zbSet;
        b && (a ? b.show() : b.hide(), this.rollOutZB())
    }, handleReleaseOutside: function (a) {
        AmCharts.AmRectangularChart.base.handleReleaseOutside.call(this,
            a);
        (a = this.chartCursor) && a.handleReleaseOutside()
    }, handleMouseDown: function (a) {
        AmCharts.AmRectangularChart.base.handleMouseDown.call(this, a);
        var b = this.chartCursor;
        b && b.handleMouseDown(a)
    }, handleCursorChange: function (a) {
    }});
AmCharts.TrendLine = AmCharts.Class({construct: function (a) {
    this.cname = "TrendLine";
    this.createEvents("click");
    this.isProtected = !1;
    this.dashLength = 0;
    this.lineColor = "#00CC00";
    this.lineThickness = this.lineAlpha = 1;
    AmCharts.applyTheme(this, a, this.cname)
}, draw: function () {
    var a = this;
    a.destroy();
    var b = a.chart, c = b.container, d, f, e, g, h = a.categoryAxis, k = a.initialDate, l = a.initialCategory, m = a.finalDate, p = a.finalCategory, n = a.valueAxis, q = a.valueAxisX, s = a.initialXValue, r = a.finalXValue, u = a.initialValue, v = a.finalValue,
        t = n.recalculateToPercents, w = b.dataDateFormat;
    h && (k && (k instanceof Date || (k = w ? AmCharts.stringToDate(k, w) : new Date(k)), a.initialDate = k, d = h.dateToCoordinate(k)), l && (d = h.categoryToCoordinate(l)), m && (m instanceof Date || (m = w ? AmCharts.stringToDate(m, w) : new Date(m)), a.finalDate = m, f = h.dateToCoordinate(m)), p && (f = h.categoryToCoordinate(p)));
    q && !t && (isNaN(s) || (d = q.getCoordinate(s)), isNaN(r) || (f = q.getCoordinate(r)));
    n && !t && (isNaN(u) || (e = n.getCoordinate(u)), isNaN(v) || (g = n.getCoordinate(v)));
    isNaN(d) || isNaN(f) ||
        isNaN(e) || isNaN(e) || (b.rotate ? (h = [e, g], f = [d, f]) : (h = [d, f], f = [e, g]), e = a.lineColor, d = AmCharts.line(c, h, f, e, a.lineAlpha, a.lineThickness, a.dashLength), g = h, k = f, p = h[1] - h[0], n = f[1] - f[0], 0 === p && (p = 0.01), 0 === n && (n = 0.01), l = p / Math.abs(p), m = n / Math.abs(n), n = p * n / Math.abs(p * n) * Math.sqrt(Math.pow(p, 2) + Math.pow(n, 2)), p = Math.asin(p / n), n = 90 * Math.PI / 180 - p, p = Math.abs(5 * Math.cos(n)), n = Math.abs(5 * Math.sin(n)), g.push(h[1] - l * n, h[0] - l * n), k.push(f[1] + m * p, f[0] + m * p), h = AmCharts.polygon(c, g, k, e, 0.005, 0), c = c.set([h, d]), c.translate(b.marginLeftReal,
        b.marginTopReal), b.trendLinesSet.push(c), a.line = d, a.set = c, h.mouseup(function () {
        a.handleLineClick()
    }).mouseover(function () {
        a.handleLineOver()
    }).mouseout(function () {
        a.handleLineOut()
    }), h.touchend && h.touchend(function () {
        a.handleLineClick()
    }))
}, handleLineClick: function () {
    var a = {type: "click", trendLine: this, chart: this.chart};
    this.fire(a.type, a)
}, handleLineOver: function () {
    var a = this.rollOverColor;
    void 0 !== a && this.line.attr({stroke: a})
}, handleLineOut: function () {
    this.line.attr({stroke: this.lineColor})
}, destroy: function () {
    AmCharts.remove(this.set)
}});
AmCharts.circle = function (a, b, c, d, f, e, g, h) {
    if (void 0 == f || 0 === f)f = 0.01;
    void 0 === e && (e = "#000000");
    void 0 === g && (g = 0);
    d = {fill: c, stroke: e, "fill-opacity": d, "stroke-width": f, "stroke-opacity": g};
    a = a.circle(0, 0, b).attr(d);
    h && a.gradient("radialGradient", [c, AmCharts.adjustLuminosity(c, -0.6)]);
    return a
};
AmCharts.text = function (a, b, c, d, f, e, g, h) {
    e || (e = "middle");
    "right" == e && (e = "end");
    isNaN(h) && (h = 1);
    void 0 !== b && (b = String(b), AmCharts.isIE && !AmCharts.isModern && (b = b.replace("&amp;", "&"), b = b.replace("&", "&amp;")));
    c = {fill: c, "font-family": d, "font-size": f, opacity: h};
    !0 === g && (c["font-weight"] = "bold");
    c["text-anchor"] = e;
    return a.text(b, c)
};
AmCharts.polygon = function (a, b, c, d, f, e, g, h, k, l, m) {
    isNaN(e) && (e = 0.01);
    isNaN(h) && (h = f);
    var p = d, n = !1;
    "object" == typeof p && 1 < p.length && (n = !0, p = p[0]);
    void 0 === g && (g = p);
    f = {fill: p, stroke: g, "fill-opacity": f, "stroke-width": e, "stroke-opacity": h};
    void 0 !== m && 0 < m && (f["stroke-dasharray"] = m);
    m = AmCharts.dx;
    e = AmCharts.dy;
    a.handDrawn && (c = AmCharts.makeHD(b, c, a.handDrawScatter), b = c[0], c = c[1]);
    g = Math.round;
    l && (g = AmCharts.doNothing);
    l = "M" + (g(b[0]) + m) + "," + (g(c[0]) + e);
    for (h = 1; h < b.length; h++)l += " L" + (g(b[h]) + m) + "," + (g(c[h]) +
        e);
    a = a.path(l + " Z").attr(f);
    n && a.gradient("linearGradient", d, k);
    return a
};
AmCharts.rect = function (a, b, c, d, f, e, g, h, k, l, m) {
    isNaN(e) && (e = 0);
    void 0 === k && (k = 0);
    void 0 === l && (l = 270);
    isNaN(f) && (f = 0);
    var p = d, n = !1;
    "object" == typeof p && (p = p[0], n = !0);
    void 0 === g && (g = p);
    void 0 === h && (h = f);
    b = Math.round(b);
    c = Math.round(c);
    var q = 0, s = 0;
    0 > b && (b = Math.abs(b), q = -b);
    0 > c && (c = Math.abs(c), s = -c);
    q += AmCharts.dx;
    s += AmCharts.dy;
    f = {fill: p, stroke: g, "fill-opacity": f, "stroke-opacity": h};
    void 0 !== m && 0 < m && (f["stroke-dasharray"] = m);
    a = a.rect(q, s, b, c, k, e).attr(f);
    n && a.gradient("linearGradient", d, l);
    return a
};
AmCharts.bullet = function (a, b, c, d, f, e, g, h, k, l, m) {
    var p;
    "circle" == b && (b = "round");
    switch (b) {
        case "round":
            p = AmCharts.circle(a, c / 2, d, f, e, g, h);
            break;
        case "square":
            p = AmCharts.polygon(a, [-c / 2, c / 2, c / 2, -c / 2], [c / 2, c / 2, -c / 2, -c / 2], d, f, e, g, h, l - 180);
            break;
        case "rectangle":
            p = AmCharts.polygon(a, [-c, c, c, -c], [c / 2, c / 2, -c / 2, -c / 2], d, f, e, g, h, l - 180);
            break;
        case "diamond":
            p = AmCharts.polygon(a, [-c / 2, 0, c / 2, 0], [0, -c / 2, 0, c / 2], d, f, e, g, h);
            break;
        case "triangleUp":
            p = AmCharts.triangle(a, c, 0, d, f, e, g, h);
            break;
        case "triangleDown":
            p = AmCharts.triangle(a,
                c, 180, d, f, e, g, h);
            break;
        case "triangleLeft":
            p = AmCharts.triangle(a, c, 270, d, f, e, g, h);
            break;
        case "triangleRight":
            p = AmCharts.triangle(a, c, 90, d, f, e, g, h);
            break;
        case "bubble":
            p = AmCharts.circle(a, c / 2, d, f, e, g, h, !0);
            break;
        case "yError":
            p = a.set();
            p.push(AmCharts.line(a, [0, 0], [-c / 2, c / 2], d, f, e));
            p.push(AmCharts.line(a, [-k, k], [-c / 2, -c / 2], d, f, e));
            p.push(AmCharts.line(a, [-k, k], [c / 2, c / 2], d, f, e));
            break;
        case "xError":
            p = a.set(), p.push(AmCharts.line(a, [-c / 2, c / 2], [0, 0], d, f, e)), p.push(AmCharts.line(a, [-c / 2, -c / 2], [-k, k],
                d, f, e)), p.push(AmCharts.line(a, [c / 2, c / 2], [-k, k], d, f, e))
    }
    p && p.pattern(m);
    return p
};
AmCharts.triangle = function (a, b, c, d, f, e, g, h) {
    if (void 0 === e || 0 === e)e = 1;
    void 0 === g && (g = "#000");
    void 0 === h && (h = 0);
    d = {fill: d, stroke: g, "fill-opacity": f, "stroke-width": e, "stroke-opacity": h};
    b /= 2;
    var k;
    0 === c && (k = " M" + -b + "," + b + " L0," + -b + " L" + b + "," + b + " Z");
    180 == c && (k = " M" + -b + "," + -b + " L0," + b + " L" + b + "," + -b + " Z");
    90 == c && (k = " M" + -b + "," + -b + " L" + b + ",0 L" + -b + "," + b + " Z");
    270 == c && (k = " M" + -b + ",0 L" + b + "," + b + " L" + b + "," + -b + " Z");
    return a.path(k).attr(d)
};
AmCharts.line = function (a, b, c, d, f, e, g, h, k, l, m) {
    if (a.handDrawn && !m)return AmCharts.handDrawnLine(a, b, c, d, f, e, g, h, k, l, m);
    e = {fill: "none", "stroke-width": e};
    void 0 !== g && 0 < g && (e["stroke-dasharray"] = g);
    isNaN(f) || (e["stroke-opacity"] = f);
    d && (e.stroke = d);
    d = Math.round;
    l && (d = AmCharts.doNothing);
    l = AmCharts.dx;
    f = AmCharts.dy;
    g = "M" + (d(b[0]) + l) + "," + (d(c[0]) + f);
    for (h = 1; h < b.length; h++)g += " L" + (d(b[h]) + l) + "," + (d(c[h]) + f);
    if (AmCharts.VML)return a.path(g, void 0, !0).attr(e);
    k && (g += " M0,0 L0,0");
    return a.path(g).attr(e)
};
AmCharts.makeHD = function (a, b, c) {
    for (var d = [], f = [], e = 1; e < a.length; e++)for (var g = Number(a[e - 1]), h = Number(b[e - 1]), k = Number(a[e]), l = Number(b[e]), m = Math.sqrt(Math.pow(k - g, 2) + Math.pow(l - h, 2)), m = Math.round(m / 50) + 1, k = (k - g) / m, l = (l - h) / m, p = 0; p <= m; p++) {
        var n = g + p * k + Math.random() * c, q = h + p * l + Math.random() * c;
        d.push(n);
        f.push(q)
    }
    return[d, f]
};
AmCharts.handDrawnLine = function (a, b, c, d, f, e, g, h, k, l, m) {
    var p = a.set();
    for (m = 1; m < b.length; m++)for (var n = [b[m - 1], b[m]], q = [c[m - 1], c[m]], q = AmCharts.makeHD(n, q, a.handDrawScatter), n = q[0], q = q[1], s = 1; s < n.length; s++)p.push(AmCharts.line(a, [n[s - 1], n[s]], [q[s - 1], q[s]], d, f, e + Math.random() * a.handDrawThickness - a.handDrawThickness / 2, g, h, k, l, !0));
    return p
};
AmCharts.doNothing = function (a) {
    return a
};
AmCharts.wedge = function (a, b, c, d, f, e, g, h, k, l, m, p) {
    var n = Math.round;
    e = n(e);
    g = n(g);
    h = n(h);
    var q = n(g / e * h), s = AmCharts.VML, r = 359.5 + e / 100;
    359.94 < r && (r = 359.94);
    f >= r && (f = r);
    var u = 1 / 180 * Math.PI, r = b + Math.sin(d * u) * h, v = c - Math.cos(d * u) * q, t = b + Math.sin(d * u) * e, w = c - Math.cos(d * u) * g, z = b + Math.sin((d + f) * u) * e, F = c - Math.cos((d + f) * u) * g, y = b + Math.sin((d + f) * u) * h, u = c - Math.cos((d + f) * u) * q, B = {fill: AmCharts.adjustLuminosity(l.fill, -0.2), "stroke-opacity": 0, "fill-opacity": l["fill-opacity"]}, G = 0;
    180 < Math.abs(f) && (G = 1);
    d = a.set();
    var K;
    s && (r = n(10 * r), t = n(10 * t), z = n(10 * z), y = n(10 * y), v = n(10 * v), w = n(10 * w), F = n(10 * F), u = n(10 * u), b = n(10 * b), k = n(10 * k), c = n(10 * c), e *= 10, g *= 10, h *= 10, q *= 10, 1 > Math.abs(f) && 1 >= Math.abs(z - t) && 1 >= Math.abs(F - w) && (K = !0));
    f = "";
    var A;
    p && (B["fill-opacity"] = 0, B["stroke-opacity"] = l["stroke-opacity"] / 2, B.stroke = l.stroke);
    0 < k && (s ? (A = " M" + r + "," + (v + k) + " L" + t + "," + (w + k), K || (A += " A" + (b - e) + "," + (k + c - g) + "," + (b + e) + "," + (k + c + g) + "," + t + "," + (w + k) + "," + z + "," + (F + k)), A += " L" + y + "," + (u + k), 0 < h && (K || (A += " B" + (b - h) + "," + (k + c - q) + "," + (b + h) + "," + (k + c + q) +
        "," + y + "," + (k + u) + "," + r + "," + (k + v)))) : (A = " M" + r + "," + (v + k) + " L" + t + "," + (w + k) + (" A" + e + "," + g + ",0," + G + ",1," + z + "," + (F + k) + " L" + y + "," + (u + k)), 0 < h && (A += " A" + h + "," + q + ",0," + G + ",0," + r + "," + (v + k))), A += " Z", A = a.path(A, void 0, void 0, "1000,1000").attr(B), d.push(A), A = a.path(" M" + r + "," + v + " L" + r + "," + (v + k) + " L" + t + "," + (w + k) + " L" + t + "," + w + " L" + r + "," + v + " Z", void 0, void 0, "1000,1000").attr(B), k = a.path(" M" + z + "," + F + " L" + z + "," + (F + k) + " L" + y + "," + (u + k) + " L" + y + "," + u + " L" + z + "," + F + " Z", void 0, void 0, "1000,1000").attr(B), d.push(A), d.push(k));
    s ? (K || (f = " A" + n(b - e) + "," + n(c - g) + "," + n(b + e) + "," + n(c + g) + "," + n(t) + "," + n(w) + "," + n(z) + "," + n(F)), e = " M" + n(r) + "," + n(v) + " L" + n(t) + "," + n(w) + f + " L" + n(y) + "," + n(u)) : e = " M" + r + "," + v + " L" + t + "," + w + (" A" + e + "," + g + ",0," + G + ",1," + z + "," + F) + " L" + y + "," + u;
    0 < h && (s ? K || (e += " B" + (b - h) + "," + (c - q) + "," + (b + h) + "," + (c + q) + "," + y + "," + u + "," + r + "," + v) : e += " A" + h + "," + q + ",0," + G + ",0," + r + "," + v);
    a.handDrawn && (b = AmCharts.line(a, [r, t], [v, w], l.stroke, l.thickness * Math.random() * a.handDrawThickness, l["stroke-opacity"]), d.push(b));
    a = a.path(e + " Z", void 0,
        void 0, "1000,1000").attr(l);
    if (m) {
        b = [];
        for (c = 0; c < m.length; c++)b.push(AmCharts.adjustLuminosity(l.fill, m[c]));
        0 < b.length && a.gradient("linearGradient", b)
    }
    a.pattern(p);
    d.push(a);
    return d
};
AmCharts.adjustLuminosity = function (a, b) {
    a = String(a).replace(/[^0-9a-f]/gi, "");
    6 > a.length && (a = String(a[0]) + String(a[0]) + String(a[1]) + String(a[1]) + String(a[2]) + String(a[2]));
    b = b || 0;
    var c = "#", d, f;
    for (f = 0; 3 > f; f++)d = parseInt(a.substr(2 * f, 2), 16), d = Math.round(Math.min(Math.max(0, d + d * b), 255)).toString(16), c += ("00" + d).substr(d.length);
    return c
};
AmCharts.Bezier = AmCharts.Class({construct: function (a, b, c, d, f, e, g, h, k, l) {
    "object" == typeof g && (g = g[0]);
    "object" == typeof h && (h = h[0]);
    e = {fill: g, "fill-opacity": h, "stroke-width": e};
    void 0 !== k && 0 < k && (e["stroke-dasharray"] = k);
    isNaN(f) || (e["stroke-opacity"] = f);
    d && (e.stroke = d);
    d = "M" + Math.round(b[0]) + "," + Math.round(c[0]);
    f = [];
    for (k = 0; k < b.length; k++)f.push({x: Number(b[k]), y: Number(c[k])});
    1 < f.length && (b = this.interpolate(f), d += this.drawBeziers(b));
    l ? d += l : AmCharts.VML || (d += "M0,0 L0,0");
    this.path = a.path(d).attr(e)
},
    interpolate: function (a) {
        var b = [];
        b.push({x: a[0].x, y: a[0].y});
        var c = a[1].x - a[0].x, d = a[1].y - a[0].y, f = AmCharts.bezierX, e = AmCharts.bezierY;
        b.push({x: a[0].x + c / f, y: a[0].y + d / e});
        var g;
        for (g = 1; g < a.length - 1; g++) {
            var h = a[g - 1], k = a[g], d = a[g + 1];
            isNaN(d.x) && (d = k);
            isNaN(k.x) && (k = h);
            isNaN(h.x) && (h = k);
            c = d.x - k.x;
            d = d.y - h.y;
            h = k.x - h.x;
            h > c && (h = c);
            b.push({x: k.x - h / f, y: k.y - d / e});
            b.push({x: k.x, y: k.y});
            b.push({x: k.x + h / f, y: k.y + d / e})
        }
        d = a[a.length - 1].y - a[a.length - 2].y;
        c = a[a.length - 1].x - a[a.length - 2].x;
        b.push({x: a[a.length - 1].x -
            c / f, y: a[a.length - 1].y - d / e});
        b.push({x: a[a.length - 1].x, y: a[a.length - 1].y});
        return b
    }, drawBeziers: function (a) {
        var b = "", c;
        for (c = 0; c < (a.length - 1) / 3; c++)b += this.drawBezierMidpoint(a[3 * c], a[3 * c + 1], a[3 * c + 2], a[3 * c + 3]);
        return b
    }, drawBezierMidpoint: function (a, b, c, d) {
        var f = Math.round, e = this.getPointOnSegment(a, b, 0.75), g = this.getPointOnSegment(d, c, 0.75), h = (d.x - a.x) / 16, k = (d.y - a.y) / 16, l = this.getPointOnSegment(a, b, 0.375);
        a = this.getPointOnSegment(e, g, 0.375);
        a.x -= h;
        a.y -= k;
        b = this.getPointOnSegment(g, e, 0.375);
        b.x +=
            h;
        b.y += k;
        c = this.getPointOnSegment(d, c, 0.375);
        h = this.getMiddle(l, a);
        e = this.getMiddle(e, g);
        g = this.getMiddle(b, c);
        l = " Q" + f(l.x) + "," + f(l.y) + "," + f(h.x) + "," + f(h.y);
        l += " Q" + f(a.x) + "," + f(a.y) + "," + f(e.x) + "," + f(e.y);
        l += " Q" + f(b.x) + "," + f(b.y) + "," + f(g.x) + "," + f(g.y);
        return l += " Q" + f(c.x) + "," + f(c.y) + "," + f(d.x) + "," + f(d.y)
    }, getMiddle: function (a, b) {
        return{x: (a.x + b.x) / 2, y: (a.y + b.y) / 2}
    }, getPointOnSegment: function (a, b, c) {
        return{x: a.x + (b.x - a.x) * c, y: a.y + (b.y - a.y) * c}
    }});
AmCharts.AmDraw = AmCharts.Class({construct: function (a, b, c, d) {
    AmCharts.SVG_NS = "http://www.w3.org/2000/svg";
    AmCharts.SVG_XLINK = "http://www.w3.org/1999/xlink";
    AmCharts.hasSVG = !!document.createElementNS && !!document.createElementNS(AmCharts.SVG_NS, "svg").createSVGRect;
    1 > b && (b = 10);
    1 > c && (c = 10);
    this.div = a;
    this.width = b;
    this.height = c;
    this.rBin = document.createElement("div");
    if (AmCharts.hasSVG) {
        AmCharts.SVG = !0;
        var f = this.createSvgElement("svg");
        f.style.position = "absolute";
        f.style.width = b + "px";
        f.style.height = c +
            "px";
        b = this.createSvgElement("desc");
        b.appendChild(document.createTextNode("JavaScript chart by amCharts " + d.version));
        f.appendChild(b);
        AmCharts.rtl && (f.setAttribute("direction", "rtl"), f.style.left = "auto", f.style.right = "0px");
        f.setAttribute("version", "1.1");
        a.appendChild(f);
        this.container = f;
        this.R = new AmCharts.SVGRenderer(this)
    } else AmCharts.isIE && AmCharts.VMLRenderer && (AmCharts.VML = !0, AmCharts.vmlStyleSheet || (document.namespaces.add("amvml", "urn:schemas-microsoft-com:vml"), 31 > document.styleSheets.length ?
        (f = document.createStyleSheet(), f.addRule(".amvml", "behavior:url(#default#VML); display:inline-block; antialias:true"), AmCharts.vmlStyleSheet = f) : document.styleSheets[0].addRule(".amvml", "behavior:url(#default#VML); display:inline-block; antialias:true")), this.container = a, this.R = new AmCharts.VMLRenderer(this, d), this.R.disableSelection(a))
}, createSvgElement: function (a) {
    return document.createElementNS(AmCharts.SVG_NS, a)
}, circle: function (a, b, c, d) {
    var f = new AmCharts.AmDObject("circle", this);
    f.attr({r: c,
        cx: a, cy: b});
    this.addToContainer(f.node, d);
    return f
}, setSize: function (a, b) {
    0 < a && 0 < b && (this.container.style.width = a + "px", this.container.style.height = b + "px")
}, rect: function (a, b, c, d, f, e, g) {
    var h = new AmCharts.AmDObject("rect", this);
    AmCharts.VML && (f = 100 * f / Math.min(c, d), c += 2 * e, d += 2 * e, h.bw = e, h.node.style.marginLeft = -e, h.node.style.marginTop = -e);
    1 > c && (c = 1);
    1 > d && (d = 1);
    h.attr({x: a, y: b, width: c, height: d, rx: f, ry: f, "stroke-width": e});
    this.addToContainer(h.node, g);
    return h
}, image: function (a, b, c, d, f, e) {
    var g = new AmCharts.AmDObject("image",
        this);
    g.attr({x: b, y: c, width: d, height: f});
    this.R.path(g, a);
    this.addToContainer(g.node, e);
    return g
}, addToContainer: function (a, b) {
    b || (b = this.container);
    b.appendChild(a)
}, text: function (a, b, c) {
    return this.R.text(a, b, c)
}, path: function (a, b, c, d) {
    var f = new AmCharts.AmDObject("path", this);
    d || (d = "100,100");
    f.attr({cs: d});
    c ? f.attr({dd: a}) : f.attr({d: a});
    this.addToContainer(f.node, b);
    return f
}, set: function (a) {
    return this.R.set(a)
}, remove: function (a) {
    if (a) {
        var b = this.rBin;
        b.appendChild(a);
        b.innerHTML = ""
    }
}, renderFix: function () {
    var a =
        this.container, b = a.style, c;
    try {
        c = a.getScreenCTM() || a.createSVGMatrix()
    } catch (d) {
        c = a.createSVGMatrix()
    }
    a = 1 - c.e % 1;
    c = 1 - c.f % 1;
    0.5 < a && (a -= 1);
    0.5 < c && (c -= 1);
    a && (b.left = a + "px");
    c && (b.top = c + "px")
}, update: function () {
    this.R.update()
}});
AmCharts.AmDObject = AmCharts.Class({construct: function (a, b) {
    this.D = b;
    this.R = b.R;
    this.node = this.R.create(this, a);
    this.y = this.x = 0;
    this.scale = 1
}, attr: function (a) {
    this.R.attr(this, a);
    return this
}, getAttr: function (a) {
    return this.node.getAttribute(a)
}, setAttr: function (a, b) {
    this.R.setAttr(this, a, b);
    return this
}, clipRect: function (a, b, c, d) {
    this.R.clipRect(this, a, b, c, d)
}, translate: function (a, b, c, d) {
    d || (a = Math.round(a), b = Math.round(b));
    this.R.move(this, a, b, c);
    this.x = a;
    this.y = b;
    this.scale = c;
    this.angle && this.rotate(this.angle)
},
    rotate: function (a, b) {
        this.R.rotate(this, a, b);
        this.angle = a
    }, animate: function (a, b, c) {
        for (var d in a)if (a.hasOwnProperty(d)) {
            var f = d, e = a[d];
            c = AmCharts.getEffect(c);
            this.R.animate(this, f, e, b, c)
        }
    }, push: function (a) {
        if (a) {
            var b = this.node;
            b.appendChild(a.node);
            var c = a.clipPath;
            c && b.appendChild(c);
            (a = a.grad) && b.appendChild(a)
        }
    }, text: function (a) {
        this.R.setText(this, a)
    }, remove: function () {
        this.R.remove(this)
    }, clear: function () {
        var a = this.node;
        if (a.hasChildNodes())for (; 1 <= a.childNodes.length;)a.removeChild(a.firstChild)
    },
    hide: function () {
        this.setAttr("visibility", "hidden")
    }, show: function () {
        this.setAttr("visibility", "visible")
    }, getBBox: function () {
        return this.R.getBBox(this)
    }, toFront: function () {
        var a = this.node;
        if (a) {
            this.prevNextNode = a.nextSibling;
            var b = a.parentNode;
            b && b.appendChild(a)
        }
    }, toPrevious: function () {
        var a = this.node;
        a && this.prevNextNode && (a = a.parentNode) && a.insertBefore(this.prevNextNode, null)
    }, toBack: function () {
        var a = this.node;
        if (a) {
            this.prevNextNode = a.nextSibling;
            var b = a.parentNode;
            if (b) {
                var c = b.firstChild;
                c && b.insertBefore(a, c)
            }
        }
    }, mouseover: function (a) {
        this.R.addListener(this, "mouseover", a);
        return this
    }, mouseout: function (a) {
        this.R.addListener(this, "mouseout", a);
        return this
    }, click: function (a) {
        this.R.addListener(this, "click", a);
        return this
    }, dblclick: function (a) {
        this.R.addListener(this, "dblclick", a);
        return this
    }, mousedown: function (a) {
        this.R.addListener(this, "mousedown", a);
        return this
    }, mouseup: function (a) {
        this.R.addListener(this, "mouseup", a);
        return this
    }, touchstart: function (a) {
        this.R.addListener(this,
            "touchstart", a);
        return this
    }, touchend: function (a) {
        this.R.addListener(this, "touchend", a);
        return this
    }, contextmenu: function (a) {
        this.node.addEventListener ? this.node.addEventListener("contextmenu", a, !0) : this.R.addListener(this, "contextmenu", a);
        return this
    }, stop: function (a) {
        (a = this.animationX) && AmCharts.removeFromArray(this.R.animations, a);
        (a = this.animationY) && AmCharts.removeFromArray(this.R.animations, a)
    }, length: function () {
        return this.node.childNodes.length
    }, gradient: function (a, b, c) {
        this.R.gradient(this,
            a, b, c)
    }, pattern: function (a, b) {
        a && this.R.pattern(this, a, b)
    }});
AmCharts.VMLRenderer = AmCharts.Class({construct: function (a, b) {
    this.chart = b;
    this.D = a;
    this.cNames = {circle: "oval", rect: "roundrect", path: "shape"};
    this.styleMap = {x: "left", y: "top", width: "width", height: "height", "font-family": "fontFamily", "font-size": "fontSize", visibility: "visibility"}
}, create: function (a, b) {
    var c;
    if ("group" == b)c = document.createElement("div"), a.type = "div"; else if ("text" == b)c = document.createElement("div"), a.type = "text"; else if ("image" == b)c = document.createElement("img"), a.type = "image"; else {
        a.type =
            "shape";
        a.shapeType = this.cNames[b];
        c = document.createElement("amvml:" + this.cNames[b]);
        var d = document.createElement("amvml:stroke");
        c.appendChild(d);
        a.stroke = d;
        var f = document.createElement("amvml:fill");
        c.appendChild(f);
        a.fill = f;
        f.className = "amvml";
        d.className = "amvml";
        c.className = "amvml"
    }
    c.style.position = "absolute";
    c.style.top = 0;
    c.style.left = 0;
    return c
}, path: function (a, b) {
    a.node.setAttribute("src", b)
}, setAttr: function (a, b, c) {
    if (void 0 !== c) {
        var d;
        8 === document.documentMode && (d = !0);
        var f = a.node, e = a.type,
            g = f.style;
        "r" == b && (g.width = 2 * c, g.height = 2 * c);
        "roundrect" != a.shapeType || "width" != b && "height" != b || (c -= 1);
        "cursor" == b && (g.cursor = c);
        "cx" == b && (g.left = c - AmCharts.removePx(g.width) / 2);
        "cy" == b && (g.top = c - AmCharts.removePx(g.height) / 2);
        var h = this.styleMap[b];
        void 0 !== h && (g[h] = c);
        "text" == e && ("text-anchor" == b && (a.anchor = c, h = f.clientWidth, "end" == c && (g.marginLeft = -h + "px"), "middle" == c && (g.marginLeft = -(h / 2) + "px", g.textAlign = "center"), "start" == c && (g.marginLeft = "0px")), "fill" == b && (g.color = c), "font-weight" == b && (g.fontWeight =
            c));
        if (g = a.children)for (h = 0; h < g.length; h++)g[h].setAttr(b, c);
        if ("shape" == e) {
            "cs" == b && (f.style.width = "100px", f.style.height = "100px", f.setAttribute("coordsize", c));
            "d" == b && f.setAttribute("path", this.svgPathToVml(c));
            "dd" == b && f.setAttribute("path", c);
            e = a.stroke;
            a = a.fill;
            "stroke" == b && (d ? e.color = c : e.setAttribute("color", c));
            "stroke-width" == b && (d ? e.weight = c : e.setAttribute("weight", c));
            "stroke-opacity" == b && (d ? e.opacity = c : e.setAttribute("opacity", c));
            "stroke-dasharray" == b && (g = "solid", 0 < c && 3 > c && (g = "dot"),
                3 <= c && 6 >= c && (g = "dash"), 6 < c && (g = "longdash"), d ? e.dashstyle = g : e.setAttribute("dashstyle", g));
            if ("fill-opacity" == b || "opacity" == b)0 === c ? d ? a.on = !1 : a.setAttribute("on", !1) : d ? a.opacity = c : a.setAttribute("opacity", c);
            "fill" == b && (d ? a.color = c : a.setAttribute("color", c));
            "rx" == b && (d ? f.arcSize = c + "%" : f.setAttribute("arcsize", c + "%"))
        }
    }
}, attr: function (a, b) {
    for (var c in b)b.hasOwnProperty(c) && this.setAttr(a, c, b[c])
}, text: function (a, b, c) {
    var d = new AmCharts.AmDObject("text", this.D), f = d.node;
    f.style.whiteSpace = "pre";
    f.innerHTML =
        a;
    this.D.addToContainer(f, c);
    this.attr(d, b);
    return d
}, getBBox: function (a) {
    return this.getBox(a.node)
}, getBox: function (a) {
    var b = a.offsetLeft, c = a.offsetTop, d = a.offsetWidth, f = a.offsetHeight, e;
    if (a.hasChildNodes()) {
        var g, h, k;
        for (k = 0; k < a.childNodes.length; k++) {
            e = this.getBox(a.childNodes[k]);
            var l = e.x;
            isNaN(l) || (isNaN(g) ? g = l : l < g && (g = l));
            var m = e.y;
            isNaN(m) || (isNaN(h) ? h = m : m < h && (h = m));
            l = e.width + l;
            isNaN(l) || (d = Math.max(d, l));
            e = e.height + m;
            isNaN(e) || (f = Math.max(f, e))
        }
        0 > g && (b += g);
        0 > h && (c += h)
    }
    return{x: b, y: c, width: d,
        height: f}
}, setText: function (a, b) {
    var c = a.node;
    c && (c.innerHTML = b);
    this.setAttr(a, "text-anchor", a.anchor)
}, addListener: function (a, b, c) {
    a.node["on" + b] = c
}, move: function (a, b, c) {
    var d = a.node, f = d.style;
    "text" == a.type && (c -= AmCharts.removePx(f.fontSize) / 2 - 1);
    "oval" == a.shapeType && (b -= AmCharts.removePx(f.width) / 2, c -= AmCharts.removePx(f.height) / 2);
    a = a.bw;
    isNaN(a) || (b -= a, c -= a);
    isNaN(b) || isNaN(c) || (d.style.left = b + "px", d.style.top = c + "px")
}, svgPathToVml: function (a) {
    var b = a.split(" ");
    a = "";
    var c, d = Math.round, f;
    for (f =
             0; f < b.length; f++) {
        var e = b[f], g = e.substring(0, 1), e = e.substring(1), h = e.split(","), k = d(h[0]) + "," + d(h[1]);
        "M" == g && (a += " m " + k);
        "L" == g && (a += " l " + k);
        "Z" == g && (a += " x e");
        if ("Q" == g) {
            var l = c.length, m = c[l - 1], p = h[0], n = h[1], k = h[2], q = h[3];
            c = d(c[l - 2] / 3 + 2 / 3 * p);
            m = d(m / 3 + 2 / 3 * n);
            p = d(2 / 3 * p + k / 3);
            n = d(2 / 3 * n + q / 3);
            a += " c " + c + "," + m + "," + p + "," + n + "," + k + "," + q
        }
        "A" == g && (a += " wa " + e);
        "B" == g && (a += " at " + e);
        c = h
    }
    return a
}, animate: function (a, b, c, d, f) {
    var e = a.node, g = this.chart;
    if ("translate" == b) {
        b = c.split(",");
        c = b[1];
        var h = e.offsetTop;
        g.animate(a, "left", e.offsetLeft, b[0], d, f, "px");
        g.animate(a, "top", h, c, d, f, "px")
    }
}, clipRect: function (a, b, c, d, f) {
    a = a.node;
    0 === b && 0 === c ? (a.style.width = d + "px", a.style.height = f + "px", a.style.overflow = "hidden") : a.style.clip = "rect(" + c + "px " + (b + d) + "px " + (c + f) + "px " + b + "px)"
}, rotate: function (a, b, c) {
    if (0 !== Number(b)) {
        var d = a.node;
        a = d.style;
        c || (c = this.getBGColor(d.parentNode));
        a.backgroundColor = c;
        a.paddingLeft = 1;
        c = b * Math.PI / 180;
        var f = Math.cos(c), e = Math.sin(c), g = AmCharts.removePx(a.left), h = AmCharts.removePx(a.top),
            k = d.offsetWidth, d = d.offsetHeight;
        b /= Math.abs(b);
        a.left = g + k / 2 - k / 2 * Math.cos(c) - b * d / 2 * Math.sin(c) + 3;
        a.top = h - b * k / 2 * Math.sin(c) + b * d / 2 * Math.sin(c);
        a.cssText = a.cssText + "; filter:progid:DXImageTransform.Microsoft.Matrix(M11='" + f + "', M12='" + -e + "', M21='" + e + "', M22='" + f + "', sizingmethod='auto expand');"
    }
}, getBGColor: function (a) {
    var b = "#FFFFFF";
    if (a.style) {
        var c = a.style.backgroundColor;
        "" !== c ? b = c : a.parentNode && (b = this.getBGColor(a.parentNode))
    }
    return b
}, set: function (a) {
    var b = new AmCharts.AmDObject("group", this.D);
    this.D.container.appendChild(b.node);
    if (a) {
        var c;
        for (c = 0; c < a.length; c++)b.push(a[c])
    }
    return b
}, gradient: function (a, b, c, d) {
    var f = "";
    "radialGradient" == b && (b = "gradientradial", c.reverse());
    "linearGradient" == b && (b = "gradient");
    var e;
    for (e = 0; e < c.length; e++) {
        var g = Math.round(100 * e / (c.length - 1)), f = f + (g + "% " + c[e]);
        e < c.length - 1 && (f += ",")
    }
    a = a.fill;
    90 == d ? d = 0 : 270 == d ? d = 180 : 180 == d ? d = 90 : 0 === d && (d = 270);
    8 === document.documentMode ? (a.type = b, a.angle = d) : (a.setAttribute("type", b), a.setAttribute("angle", d));
    f && (a.colors.value =
        f)
}, remove: function (a) {
    a.clipPath && this.D.remove(a.clipPath);
    this.D.remove(a.node)
}, disableSelection: function (a) {
    void 0 !== typeof a.onselectstart && (a.onselectstart = function () {
        return!1
    });
    a.style.cursor = "default"
}, pattern: function (a, b) {
    var c = a.fill;
    a.node.fillColor = "none";
    8 === document.documentMode ? (c.type = "tile", c.src = b.url) : (c.setAttribute("type", "tile"), c.setAttribute("src", b.url))
}, update: function () {
}});
AmCharts.SVGRenderer = AmCharts.Class({construct: function (a) {
    this.D = a;
    this.animations = []
}, create: function (a, b) {
    return document.createElementNS(AmCharts.SVG_NS, b)
}, attr: function (a, b) {
    for (var c in b)b.hasOwnProperty(c) && this.setAttr(a, c, b[c])
}, setAttr: function (a, b, c) {
    void 0 !== c && a.node.setAttribute(b, c)
}, animate: function (a, b, c, d, f) {
    var e = a.node;
    a["an_" + b] && AmCharts.removeFromArray(this.animations, a["an_" + b]);
    "translate" == b ? (e = (e = e.getAttribute("transform")) ? String(e).substring(10, e.length - 1) : "0,0", e =
        e.split(", ").join(" "), e = e.split(" ").join(","), 0 === e && (e = "0,0")) : e = Number(e.getAttribute(b));
    c = {obj: a, frame: 0, attribute: b, from: e, to: c, time: d, effect: f};
    this.animations.push(c);
    a["an_" + b] = c
}, update: function () {
    var a, b = this.animations;
    for (a = b.length - 1; 0 <= a; a--) {
        var c = b[a], d = 1E3 * c.time / AmCharts.updateRate, f = c.frame + 1, e = c.obj, g = c.attribute, h, k, l;
        f <= d ? (c.frame++, "translate" == g ? (h = c.from.split(","), g = Number(h[0]), h = Number(h[1]), isNaN(h) && (h = 0), k = c.to.split(","), l = Number(k[0]), k = Number(k[1]), l = 0 === l - g ? l :
            Math.round(AmCharts[c.effect](0, f, g, l - g, d)), c = 0 === k - h ? k : Math.round(AmCharts[c.effect](0, f, h, k - h, d)), g = "transform", c = "translate(" + l + "," + c + ")") : (k = Number(c.from), h = Number(c.to), l = h - k, c = AmCharts[c.effect](0, f, k, l, d), isNaN(c) && (c = h), 0 === l && this.animations.splice(a, 1)), this.setAttr(e, g, c)) : ("translate" == g ? (k = c.to.split(","), l = Number(k[0]), k = Number(k[1]), e.translate(l, k)) : (h = Number(c.to), this.setAttr(e, g, h)), this.animations.splice(a, 1))
    }
}, getBBox: function (a) {
    if (a = a.node)try {
        return a.getBBox()
    } catch (b) {
    }
    return{width: 0,
        height: 0, x: 0, y: 0}
}, path: function (a, b) {
    a.node.setAttributeNS(AmCharts.SVG_XLINK, "xlink:href", b)
}, clipRect: function (a, b, c, d, f) {
    var e = a.node, g = a.clipPath;
    g && this.D.remove(g);
    var h = e.parentNode;
    h && (e = document.createElementNS(AmCharts.SVG_NS, "clipPath"), g = AmCharts.getUniqueId(), e.setAttribute("id", g), this.D.rect(b, c, d, f, 0, 0, e), h.appendChild(e), b = "#", AmCharts.baseHref && !AmCharts.isIE && (b = window.location.href + b), this.setAttr(a, "clip-path", "url(" + b + g + ")"), this.clipPathC++, a.clipPath = e)
}, text: function (a, b, c) {
    var d = new AmCharts.AmDObject("text", this.D);
    a = String(a).split("\n");
    var f = b["font-size"], e;
    for (e = 0; e < a.length; e++) {
        var g = this.create(null, "tspan");
        g.appendChild(document.createTextNode(a[e]));
        g.setAttribute("y", (f + 2) * e + Math.round(f / 2));
        g.setAttribute("x", 0);
        d.node.appendChild(g)
    }
    d.node.setAttribute("y", Math.round(f / 2));
    this.attr(d, b);
    this.D.addToContainer(d.node, c);
    return d
}, setText: function (a, b) {
    var c = a.node;
    c && (c.removeChild(c.firstChild), c.appendChild(document.createTextNode(b)))
}, move: function (a, b, c, d) {
    b = "translate(" + b + "," + c + ")";
    d && (b = b + " scale(" + d + ")");
    this.setAttr(a, "transform", b)
}, rotate: function (a, b) {
    var c = a.node.getAttribute("transform"), d = "rotate(" + b + ")";
    c && (d = c + " " + d);
    this.setAttr(a, "transform", d)
}, set: function (a) {
    var b = new AmCharts.AmDObject("g", this.D);
    this.D.container.appendChild(b.node);
    if (a) {
        var c;
        for (c = 0; c < a.length; c++)b.push(a[c])
    }
    return b
}, addListener: function (a, b, c) {
    a.node["on" + b] = c
}, gradient: function (a, b, c, d) {
    var f = a.node, e = a.grad;
    e && this.D.remove(e);
    b = document.createElementNS(AmCharts.SVG_NS,
        b);
    e = AmCharts.getUniqueId();
    b.setAttribute("id", e);
    if (!isNaN(d)) {
        var g = 0, h = 0, k = 0, l = 0;
        90 == d ? k = 100 : 270 == d ? l = 100 : 180 == d ? g = 100 : 0 === d && (h = 100);
        b.setAttribute("x1", g + "%");
        b.setAttribute("x2", h + "%");
        b.setAttribute("y1", k + "%");
        b.setAttribute("y2", l + "%")
    }
    for (d = 0; d < c.length; d++)g = document.createElementNS(AmCharts.SVG_NS, "stop"), h = 100 * d / (c.length - 1), 0 === d && (h = 0), g.setAttribute("offset", h + "%"), g.setAttribute("stop-color", c[d]), b.appendChild(g);
    f.parentNode.appendChild(b);
    c = "#";
    AmCharts.baseHref && !AmCharts.isIE &&
    (c = window.location.href + c);
    f.setAttribute("fill", "url(" + c + e + ")");
    a.grad = b
}, pattern: function (a, b, c) {
    var d = a.node;
    isNaN(c) && (c = 1);
    var f = a.patternNode;
    f && this.D.remove(f);
    var f = document.createElementNS(AmCharts.SVG_NS, "pattern"), e = AmCharts.getUniqueId(), g = b;
    b.url && (g = b.url);
    var h = Number(b.width);
    isNaN(h) && (h = 4);
    var k = Number(b.height);
    isNaN(k) && (k = 4);
    h /= c;
    k /= c;
    c = b.x;
    isNaN(c) && (c = 0);
    var l = -Math.random() * Number(b.randomX);
    isNaN(l) || (c = l);
    l = b.y;
    isNaN(l) && (l = 0);
    b = -Math.random() * Number(b.randomY);
    isNaN(b) ||
    (l = b);
    f.setAttribute("id", e);
    f.setAttribute("width", h);
    f.setAttribute("height", k);
    f.setAttribute("patternUnits", "userSpaceOnUse");
    f.setAttribute("xlink:href", g);
    this.D.image(g, 0, 0, h, k, f).translate(c, l);
    g = "#";
    AmCharts.baseHref && !AmCharts.isIE && (g = window.location.href + g);
    d.setAttribute("fill", "url(" + g + e + ")");
    a.patternNode = f;
    d.parentNode.appendChild(f)
}, remove: function (a) {
    a.clipPath && this.D.remove(a.clipPath);
    a.grad && this.D.remove(a.grad);
    a.patternNode && this.D.remove(a.patternNode);
    this.D.remove(a.node)
}});
AmCharts.AmDSet = AmCharts.Class({construct: function (a) {
    this.create("g")
}, attr: function (a) {
    this.R.attr(this.node, a)
}, move: function (a, b) {
    this.R.move(this.node, a, b)
}});
AmCharts.AmLegend = AmCharts.Class({construct: function (a) {
    this.cname = "AmLegend";
    this.createEvents("rollOverMarker", "rollOverItem", "rollOutMarker", "rollOutItem", "showItem", "hideItem", "clickMarker", "rollOverItem", "rollOutItem", "clickLabel");
    this.position = "bottom";
    this.borderColor = this.color = "#000000";
    this.borderAlpha = 0;
    this.markerLabelGap = 5;
    this.verticalGap = 10;
    this.align = "left";
    this.horizontalGap = 0;
    this.spacing = 10;
    this.markerDisabledColor = "#AAB3B3";
    this.markerType = "square";
    this.markerSize = 16;
    this.markerBorderThickness =
        this.markerBorderAlpha = 1;
    this.marginBottom = this.marginTop = 0;
    this.marginLeft = this.marginRight = 20;
    this.autoMargins = !0;
    this.valueWidth = 50;
    this.switchable = !0;
    this.switchType = "x";
    this.switchColor = "#FFFFFF";
    this.rollOverColor = "#CC0000";
    this.reversedOrder = !1;
    this.labelText = "[[title]]";
    this.valueText = "[[value]]";
    this.useMarkerColorForLabels = !1;
    this.rollOverGraphAlpha = 1;
    this.textClickEnabled = !1;
    this.equalWidths = !0;
    this.dateFormat = "DD-MM-YYYY";
    this.backgroundColor = "#FFFFFF";
    this.backgroundAlpha = 0;
    this.useGraphSettings = !1;
    this.showEntries = !0;
    AmCharts.applyTheme(this, a, this.cname)
}, setData: function (a) {
    this.legendData = a;
    this.invalidateSize()
}, invalidateSize: function () {
    this.destroy();
    this.entries = [];
    this.valueLabels = [];
    (AmCharts.ifArray(this.legendData) || AmCharts.ifArray(this.data)) && this.drawLegend()
}, drawLegend: function () {
    var a = this.chart, b = this.position, c = this.width, d = a.divRealWidth, f = a.divRealHeight, e = this.div, g = this.legendData;
    this.data && (g = this.data);
    isNaN(this.fontSize) && (this.fontSize = a.fontSize);
    if ("right" ==
        b || "left" == b)this.maxColumns = 1, this.autoMargins && (this.marginLeft = this.marginRight = 10); else if (this.autoMargins) {
        this.marginRight = a.marginRight;
        this.marginLeft = a.marginLeft;
        var h = a.autoMarginOffset;
        "bottom" == b ? (this.marginBottom = h, this.marginTop = 0) : (this.marginTop = h, this.marginBottom = 0)
    }
    var k;
    void 0 !== c ? k = AmCharts.toCoordinate(c, d) : "right" != b && "left" != b && (k = a.realWidth);
    "outside" == b ? (k = e.offsetWidth, f = e.offsetHeight, e.clientHeight && (k = e.clientWidth, f = e.clientHeight)) : (e.style.width = k + "px", e.className =
        "amChartsLegend");
    this.divWidth = k;
    this.container = new AmCharts.AmDraw(e, k, f, a);
    this.lx = 0;
    this.ly = 8;
    b = this.markerSize;
    b > this.fontSize && (this.ly = b / 2 - 1);
    0 < b && (this.lx += b + this.markerLabelGap);
    this.titleWidth = 0;
    if (b = this.title)a = AmCharts.text(this.container, b, this.color, a.fontFamily, this.fontSize, "start", !0), a.translate(this.marginLeft, this.marginTop + this.verticalGap + this.ly + 1), a = a.getBBox(), this.titleWidth = a.width + 15, this.titleHeight = a.height + 6;
    this.index = this.maxLabelWidth = 0;
    if (this.showEntries) {
        for (a =
                 0; a < g.length; a++)this.createEntry(g[a]);
        for (a = this.index = 0; a < g.length; a++)this.createValue(g[a])
    }
    this.arrangeEntries();
    this.updateValues()
}, arrangeEntries: function () {
    var a = this.position, b = this.marginLeft + this.titleWidth, c = this.marginRight, d = this.marginTop, f = this.marginBottom, e = this.horizontalGap, g = this.div, h = this.divWidth, k = this.maxColumns, l = this.verticalGap, m = this.spacing, p = h - c - b, n = 0, q = 0, s = this.container, r = s.set();
    this.set = r;
    s = s.set();
    r.push(s);
    var u = this.entries, v, t;
    for (t = 0; t < u.length; t++) {
        v = u[t].getBBox();
        var w = v.width;
        w > n && (n = w);
        v = v.height;
        v > q && (q = v)
    }
    var z = w = 0, F = e;
    for (t = 0; t < u.length; t++) {
        var y = u[t];
        this.reversedOrder && (y = u[u.length - t - 1]);
        v = y.getBBox();
        var B;
        this.equalWidths ? B = e + z * (n + m + this.markerLabelGap) : (B = F, F = F + v.width + e + m);
        B + v.width > p && 0 < t && 0 !== z && (w++, z = 0, B = e, F = B + v.width + e + m);
        y.translate(B, (q + l) * w);
        z++;
        !isNaN(k) && z >= k && (z = 0, w++);
        s.push(y)
    }
    v = s.getBBox();
    k = v.height + 2 * l - 1;
    "left" == a || "right" == a ? (h = v.width + 2 * e, g.style.width = h + b + c + "px") : h = h - b - c - 1;
    c = AmCharts.polygon(this.container, [0, h, h, 0], [0, 0, k,
        k], this.backgroundColor, this.backgroundAlpha, 1, this.borderColor, this.borderAlpha);
    r.push(c);
    r.translate(b, d);
    c.toBack();
    b = e;
    if ("top" == a || "bottom" == a || "absolute" == a || "outside" == a)"center" == this.align ? b = e + (h - v.width) / 2 : "right" == this.align && (b = e + h - v.width);
    s.translate(b, l + 1);
    this.titleHeight > k && (k = this.titleHeight);
    a = k + d + f + 1;
    0 > a && (a = 0);
    g.style.height = Math.round(a) + "px"
}, createEntry: function (a) {
    if (!1 !== a.visibleInLegend) {
        var b = this.chart, c = a.markerType;
        c || (c = this.markerType);
        var d = a.color, f = a.alpha;
        a.legendKeyColor &&
        (d = a.legendKeyColor());
        a.legendKeyAlpha && (f = a.legendKeyAlpha());
        var e;
        !0 === a.hidden && (e = d = this.markerDisabledColor);
        var g = a.pattern, h = a.customMarker;
        h || (h = this.customMarker);
        var k = this.container, l = this.markerSize, m = 0, p = 0, n = l / 2;
        if (this.useGraphSettings)if (m = a.type, this.switchType = void 0, "line" == m || "step" == m || "smoothedLine" == m || "ohlc" == m)g = k.set(), a.hidden || (d = a.lineColorR, e = a.bulletBorderColorR), p = AmCharts.line(k, [0, 2 * l], [l / 2, l / 2], d, a.lineAlpha, a.lineThickness, a.dashLength), g.push(p), a.bullet && (a.hidden ||
            (d = a.bulletColorR), p = AmCharts.bullet(k, a.bullet, a.bulletSize, d, a.bulletAlpha, a.bulletBorderThickness, e, a.bulletBorderAlpha)) && (p.translate(l + 1, l / 2), g.push(p)), n = 0, m = l, p = l / 3; else {
            var q;
            a.getGradRotation && (q = a.getGradRotation());
            m = a.fillColorsR;
            !0 === a.hidden && (m = d);
            if (g = this.createMarker("rectangle", m, a.fillAlphas, a.lineThickness, d, a.lineAlpha, q, g))n = l, g.translate(n, l / 2);
            m = l
        } else h ? (b.path && (h = b.path + h), g = k.image(h, 0, 0, l, l)) : (g = this.createMarker(c, d, f, void 0, void 0, void 0, void 0, g)) && g.translate(l /
            2, l / 2);
        this.addListeners(g, a);
        k = k.set([g]);
        this.switchable && k.setAttr("cursor", "pointer");
        (e = this.switchType) && "none" != e && ("x" == e ? (q = this.createX(), q.translate(l / 2, l / 2)) : q = this.createV(), q.dItem = a, !0 !== a.hidden ? "x" == e ? q.hide() : q.show() : "x" != e && q.hide(), this.switchable || q.hide(), this.addListeners(q, a), a.legendSwitch = q, k.push(q));
        e = this.color;
        a.showBalloon && this.textClickEnabled && void 0 !== this.selectedColor && (e = this.selectedColor);
        this.useMarkerColorForLabels && (e = d);
        !0 === a.hidden && (e = this.markerDisabledColor);
        d = AmCharts.massReplace(this.labelText, {"[[title]]": a.title});
        q = this.fontSize;
        g && l <= q && g.translate(n, l / 2 + this.ly - q / 2 + (q + 2 - l) / 2 - p);
        var s;
        d && (d = AmCharts.fixBrakes(d), a.legendTextReal = d, s = AmCharts.text(this.container, d, e, b.fontFamily, q, "start"), s.translate(this.lx + m, this.ly), k.push(s), b = s.getBBox().width, this.maxLabelWidth < b && (this.maxLabelWidth = b));
        this.entries[this.index] = k;
        a.legendEntry = this.entries[this.index];
        a.legendLabel = s;
        this.index++
    }
}, addListeners: function (a, b) {
    var c = this;
    a && a.mouseover(function () {
        c.rollOverMarker(b)
    }).mouseout(function () {
        c.rollOutMarker(b)
    }).click(function () {
        c.clickMarker(b)
    })
},
    rollOverMarker: function (a) {
        this.switchable && this.dispatch("rollOverMarker", a);
        this.dispatch("rollOverItem", a)
    }, rollOutMarker: function (a) {
        this.switchable && this.dispatch("rollOutMarker", a);
        this.dispatch("rollOutItem", a)
    }, clickMarker: function (a) {
        this.switchable ? !0 === a.hidden ? this.dispatch("showItem", a) : this.dispatch("hideItem", a) : this.textClickEnabled && this.dispatch("clickMarker", a)
    }, rollOverLabel: function (a) {
        a.hidden || (this.textClickEnabled && a.legendLabel && a.legendLabel.attr({fill: this.rollOverColor}),
            this.dispatch("rollOverItem", a))
    }, rollOutLabel: function (a) {
        if (!a.hidden) {
            if (this.textClickEnabled && a.legendLabel) {
                var b = this.color;
                void 0 !== this.selectedColor && a.showBalloon && (b = this.selectedColor);
                this.useMarkerColorForLabels && (b = a.lineColor, void 0 === b && (b = a.color));
                a.legendLabel.attr({fill: b})
            }
            this.dispatch("rollOutItem", a)
        }
    }, clickLabel: function (a) {
        this.textClickEnabled ? a.hidden || this.dispatch("clickLabel", a) : this.switchable && (!0 === a.hidden ? this.dispatch("showItem", a) : this.dispatch("hideItem", a))
    },
    dispatch: function (a, b) {
        this.fire(a, {type: a, dataItem: b, target: this, chart: this.chart})
    }, createValue: function (a) {
        var b = this, c = b.fontSize;
        if (!1 !== a.visibleInLegend) {
            var d = b.maxLabelWidth;
            b.equalWidths || (b.valueAlign = "left");
            "left" == b.valueAlign && (d = a.legendEntry.getBBox().width);
            var f = d;
            if (b.valueText && 0 < b.valueWidth) {
                var e = b.color;
                b.useMarkerColorForValues && (e = a.color, a.legendKeyColor && (e = a.legendKeyColor()));
                !0 === a.hidden && (e = b.markerDisabledColor);
                var g = b.valueText, d = d + b.lx + b.markerLabelGap + b.valueWidth,
                    h = "end";
                "left" == b.valueAlign && (d -= b.valueWidth, h = "start");
                e = AmCharts.text(b.container, g, e, b.chart.fontFamily, c, h);
                e.translate(d, b.ly);
                b.entries[b.index].push(e);
                f += b.valueWidth + 2 * b.markerLabelGap;
                e.dItem = a;
                b.valueLabels.push(e)
            }
            b.index++;
            e = b.markerSize;
            e < c + 7 && (e = c + 7, AmCharts.VML && (e += 3));
            c = b.container.rect(b.markerSize, 0, f, e, 0, 0).attr({stroke: "none", fill: "#ffffff", "fill-opacity": 0.005});
            c.dItem = a;
            b.entries[b.index - 1].push(c);
            c.mouseover(function () {
                b.rollOverLabel(a)
            }).mouseout(function () {
                b.rollOutLabel(a)
            }).click(function () {
                b.clickLabel(a)
            })
        }
    },
    createV: function () {
        var a = this.markerSize;
        return AmCharts.polygon(this.container, [a / 5, a / 2, a - a / 5, a / 2], [a / 3, a - a / 5, a / 5, a / 1.7], this.switchColor)
    }, createX: function () {
        var a = (this.markerSize - 4) / 2, b = {stroke: this.switchColor, "stroke-width": 3}, c = this.container, d = AmCharts.line(c, [-a, a], [-a, a]).attr(b), a = AmCharts.line(c, [-a, a], [a, -a]).attr(b);
        return this.container.set([d, a])
    }, createMarker: function (a, b, c, d, f, e, g, h) {
        var k = this.markerSize, l = this.container;
        f || (f = this.markerBorderColor);
        f || (f = b);
        isNaN(d) && (d = this.markerBorderThickness);
        isNaN(e) && (e = this.markerBorderAlpha);
        return AmCharts.bullet(l, a, k, b, c, d, f, e, k, g, h)
    }, validateNow: function () {
        this.invalidateSize()
    }, updateValues: function () {
        var a = this.valueLabels, b = this.chart, c, d = this.data;
        for (c = 0; c < a.length; c++) {
            var f = a[c], e = f.dItem, g = " ";
            if (d)e.value ? f.text(e.value) : f.text(""); else {
                if (void 0 !== e.type) {
                    var h = e.currentDataItem, k = this.periodValueText;
                    e.legendPeriodValueText && (k = e.legendPeriodValueText);
                    h ? (g = this.valueText, e.legendValueText && (g = e.legendValueText), g = b.formatString(g, h)) :
                        k && (g = b.formatPeriodString(k, e))
                } else g = b.formatString(this.valueText, e);
                (h = e.legendLabel) && h.text(e.legendTextReal);
                f.text(g)
            }
        }
    }, renderFix: function () {
        if (!AmCharts.VML) {
            var a = this.container;
            a && a.renderFix()
        }
    }, destroy: function () {
        this.div.innerHTML = "";
        AmCharts.remove(this.set)
    }});
AmCharts.formatMilliseconds = function (a, b) {
    if (-1 != a.indexOf("fff")) {
        var c = b.getMilliseconds(), d = String(c);
        10 > c && (d = "00" + c);
        10 <= c && 100 > c && (d = "0" + c);
        a = a.replace(/fff/g, d)
    }
    return a
};
AmCharts.extractPeriod = function (a) {
    var b = AmCharts.stripNumbers(a), c = 1;
    b != a && (c = Number(a.slice(0, a.indexOf(b))));
    return{period: b, count: c}
};
AmCharts.resetDateToMin = function (a, b, c, d) {
    void 0 === d && (d = 1);
    var f, e, g, h, k, l, m;
    AmCharts.useUTC ? (f = a.getUTCFullYear(), e = a.getUTCMonth(), g = a.getUTCDate(), h = a.getUTCHours(), k = a.getUTCMinutes(), l = a.getUTCSeconds(), m = a.getUTCMilliseconds(), a = a.getUTCDay()) : (f = a.getFullYear(), e = a.getMonth(), g = a.getDate(), h = a.getHours(), k = a.getMinutes(), l = a.getSeconds(), m = a.getMilliseconds(), a = a.getDay());
    switch (b) {
        case "YYYY":
            f = Math.floor(f / c) * c;
            e = 0;
            g = 1;
            m = l = k = h = 0;
            break;
        case "MM":
            e = Math.floor(e / c) * c;
            g = 1;
            m = l = k = h = 0;
            break;
        case "WW":
            0 ===
                a && 0 < d && (a = 7);
            g = g - a + d;
            m = l = k = h = 0;
            break;
        case "DD":
            m = l = k = h = 0;
            break;
        case "hh":
            h = Math.floor(h / c) * c;
            m = l = k = 0;
            break;
        case "mm":
            k = Math.floor(k / c) * c;
            m = l = 0;
            break;
        case "ss":
            l = Math.floor(l / c) * c;
            m = 0;
            break;
        case "fff":
            m = Math.floor(m / c) * c
    }
    AmCharts.useUTC ? (a = new Date, a.setUTCFullYear(f, e, g), a.setUTCHours(h, k, l, m)) : a = new Date(f, e, g, h, k, l, m);
    return a
};
AmCharts.getPeriodDuration = function (a, b) {
    void 0 === b && (b = 1);
    var c;
    switch (a) {
        case "YYYY":
            c = 316224E5;
            break;
        case "MM":
            c = 26784E5;
            break;
        case "WW":
            c = 6048E5;
            break;
        case "DD":
            c = 864E5;
            break;
        case "hh":
            c = 36E5;
            break;
        case "mm":
            c = 6E4;
            break;
        case "ss":
            c = 1E3;
            break;
        case "fff":
            c = 1
    }
    return c * b
};
AmCharts.intervals = {s: {nextInterval: "ss", contains: 1E3}, ss: {nextInterval: "mm", contains: 60, count: 0}, mm: {nextInterval: "hh", contains: 60, count: 1}, hh: {nextInterval: "DD", contains: 24, count: 2}, DD: {nextInterval: "", contains: Infinity, count: 3}};
AmCharts.getMaxInterval = function (a, b) {
    var c = AmCharts.intervals;
    return a >= c[b].contains ? (a = Math.round(a / c[b].contains), b = c[b].nextInterval, AmCharts.getMaxInterval(a, b)) : "ss" == b ? c[b].nextInterval : b
};
AmCharts.dayNames = "Sunday Monday Tuesday Wednesday Thursday Friday Saturday".split(" ");
AmCharts.shortDayNames = "Sun Mon Tue Wed Thu Fri Sat".split(" ");
AmCharts.monthNames = "January February March April May June July August September October November December".split(" ");
AmCharts.shortMonthNames = "Jan Feb Mar Apr May Jun Jul Aug Sep Oct Nov Dec".split(" ");
AmCharts.getWeekNumber = function (a) {
    a = new Date(a);
    a.setHours(0, 0, 0);
    a.setDate(a.getDate() + 4 - (a.getDay() || 7));
    var b = new Date(a.getFullYear(), 0, 1);
    return Math.ceil(((a - b) / 864E5 + 1) / 7)
};
AmCharts.stringToDate = function (a, b) {
    var c = {}, d = [
        {pattern: "YYYY", period: "year"},
        {pattern: "YY", period: "year"},
        {pattern: "MM", period: "month"},
        {pattern: "M", period: "month"},
        {pattern: "DD", period: "date"},
        {pattern: "D", period: "date"},
        {pattern: "JJ", period: "hours"},
        {pattern: "J", period: "hours"},
        {pattern: "HH", period: "hours"},
        {pattern: "H", period: "hours"},
        {pattern: "KK", period: "hours"},
        {pattern: "K", period: "hours"},
        {pattern: "LL", period: "hours"},
        {pattern: "L", period: "hours"},
        {pattern: "NN", period: "minutes"},
        {pattern: "N",
            period: "minutes"},
        {pattern: "SS", period: "seconds"},
        {pattern: "S", period: "seconds"},
        {pattern: "QQQ", period: "milliseconds"},
        {pattern: "QQ", period: "milliseconds"},
        {pattern: "Q", period: "milliseconds"}
    ], f = !0, e = b.indexOf("AA");
    -1 != e && (a.substr(e, 2), "pm" == a.toLowerCase && (f = !1));
    var e = b, g, h, k;
    for (k = 0; k < d.length; k++)h = d[k].period, c[h] = 0, "date" == h && (c[h] = 1);
    for (k = 0; k < d.length; k++)if (g = d[k].pattern, h = d[k].period, -1 != b.indexOf(g)) {
        var l = AmCharts.getFromDateString(g, a, e);
        b = b.replace(g, "");
        if ("KK" == g || "K" == g || "LL" ==
            g || "L" == g)f || (l += 12);
        c[h] = l
    }
    return new Date(c.year, c.month, c.date, c.hours, c.minutes, c.seconds, c.milliseconds)
};
AmCharts.getFromDateString = function (a, b, c) {
    c = c.indexOf(a);
    b = b.substr(c, a.length);
    "0" == b.charAt(0) && (b = b.substr(1, b.length - 1));
    b = Number(b);
    isNaN(b) && (b = 0);
    -1 != a.indexOf("M") && b--;
    return b
};
AmCharts.formatDate = function (a, b) {
    var c, d, f, e, g, h, k, l, m = AmCharts.getWeekNumber(a);
    AmCharts.useUTC ? (c = a.getUTCFullYear(), d = a.getUTCMonth(), f = a.getUTCDate(), e = a.getUTCDay(), g = a.getUTCHours(), h = a.getUTCMinutes(), k = a.getUTCSeconds(), l = a.getUTCMilliseconds()) : (c = a.getFullYear(), d = a.getMonth(), f = a.getDate(), e = a.getDay(), g = a.getHours(), h = a.getMinutes(), k = a.getSeconds(), l = a.getMilliseconds());
    var p = String(c).substr(2, 2), n = d + 1;
    9 > d && (n = "0" + n);
    var q = "0" + e;
    b = b.replace(/W/g, m);
    m = g;
    24 == m && (m = 0);
    var s = m;
    10 > s && (s =
        "0" + s);
    b = b.replace(/JJ/g, s);
    b = b.replace(/J/g, m);
    s = g;
    0 === s && (s = 24, -1 != b.indexOf("H") && f--);
    m = f;
    10 > f && (m = "0" + f);
    var r = s;
    10 > r && (r = "0" + r);
    b = b.replace(/HH/g, r);
    b = b.replace(/H/g, s);
    s = g;
    11 < s && (s -= 12);
    r = s;
    10 > r && (r = "0" + r);
    b = b.replace(/KK/g, r);
    b = b.replace(/K/g, s);
    s = g;
    0 === s && (s = 12);
    12 < s && (s -= 12);
    r = s;
    10 > r && (r = "0" + r);
    b = b.replace(/LL/g, r);
    b = b.replace(/L/g, s);
    s = h;
    10 > s && (s = "0" + s);
    b = b.replace(/NN/g, s);
    b = b.replace(/N/g, h);
    h = k;
    10 > h && (h = "0" + h);
    b = b.replace(/SS/g, h);
    b = b.replace(/S/g, k);
    k = l;
    10 > k && (k = "00" + k);
    100 > k && (k = "0" +
        k);
    h = l;
    10 > h && (h = "00" + h);
    b = b.replace(/QQQ/g, k);
    b = b.replace(/QQ/g, h);
    b = b.replace(/Q/g, l);
    b = 12 > g ? b.replace(/A/g, "am") : b.replace(/A/g, "pm");
    b = b.replace(/YYYY/g, "@IIII@");
    b = b.replace(/YY/g, "@II@");
    b = b.replace(/MMMM/g, "@XXXX@");
    b = b.replace(/MMM/g, "@XXX@");
    b = b.replace(/MM/g, "@XX@");
    b = b.replace(/M/g, "@X@");
    b = b.replace(/DD/g, "@RR@");
    b = b.replace(/D/g, "@R@");
    b = b.replace(/EEEE/g, "@PPPP@");
    b = b.replace(/EEE/g, "@PPP@");
    b = b.replace(/EE/g, "@PP@");
    b = b.replace(/E/g, "@P@");
    b = b.replace(/@IIII@/g, c);
    b = b.replace(/@II@/g,
        p);
    b = b.replace(/@XXXX@/g, AmCharts.monthNames[d]);
    b = b.replace(/@XXX@/g, AmCharts.shortMonthNames[d]);
    b = b.replace(/@XX@/g, n);
    b = b.replace(/@X@/g, d + 1);
    b = b.replace(/@RR@/g, m);
    b = b.replace(/@R@/g, f);
    b = b.replace(/@PPPP@/g, AmCharts.dayNames[e]);
    b = b.replace(/@PPP@/g, AmCharts.shortDayNames[e]);
    b = b.replace(/@PP@/g, q);
    return b = b.replace(/@P@/g, e)
};
AmCharts.changeDate = function (a, b, c, d, f) {
    var e = -1;
    void 0 === d && (d = !0);
    void 0 === f && (f = !1);
    !0 === d && (e = 1);
    switch (b) {
        case "YYYY":
            a.setFullYear(a.getFullYear() + c * e);
            d || f || a.setDate(a.getDate() + 1);
            break;
        case "MM":
            b = a.getMonth();
            a.setMonth(a.getMonth() + c * e);
            a.getMonth() > b + c * e && a.setDate(a.getDate() - 1);
            d || f || a.setDate(a.getDate() + 1);
            break;
        case "DD":
            a.setDate(a.getDate() + c * e);
            break;
        case "WW":
            a.setDate(a.getDate() + c * e * 7);
            break;
        case "hh":
            a.setHours(a.getHours() + c * e);
            break;
        case "mm":
            a.setMinutes(a.getMinutes() +
                c * e);
            break;
        case "ss":
            a.setSeconds(a.getSeconds() + c * e);
            break;
        case "fff":
            a.setMilliseconds(a.getMilliseconds() + c * e)
    }
    return a
};