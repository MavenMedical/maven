AmCharts.GaugeAxis = AmCharts.Class({construct: function (a) {
    this.cname = "GaugeAxis";
    this.radius = "95%";
    this.startAngle = -120;
    this.endAngle = 120;
    this.startValue = 0;
    this.endValue = 200;
    this.valueInterval = 20;
    this.minorTickInterval = 5;
    this.tickLength = 10;
    this.minorTickLength = 5;
    this.tickColor = "#555555";
    this.labelFrequency = this.tickThickness = this.tickAlpha = 1;
    this.inside = !0;
    this.labelOffset = 10;
    this.showLastLabel = this.showFirstLabel = !0;
    this.axisThickness = 1;
    this.axisColor = "#000000";
    this.axisAlpha = 1;
    this.gridInside = !0;
    this.topTextYOffset = 0;
    this.topTextBold = !0;
    this.bottomTextYOffset = 0;
    this.bottomTextBold = !0;
    this.centerY = this.centerX = "0%";
    this.bandOutlineAlpha = this.bandOutlineThickness = 0;
    this.bandOutlineColor = "#000000";
    this.bandAlpha = 1;
    AmCharts.applyTheme(this, a, "GaugeAxis")
}, value2angle: function (a) {
    return this.startAngle + this.singleValueAngle * a
}, setTopText: function (a) {
    if (void 0 !== a) {
        this.topText = a;
        var b = this.chart;
        if (this.axisCreated) {
            this.topTF && this.topTF.remove();
            var d = this.topTextFontSize;
            d || (d = b.fontSize);
            var c = this.topTextColor;
            c || (c = b.color);
            a = AmCharts.text(b.container, a, c, b.fontFamily, d, void 0, this.topTextBold);
            a.translate(this.centerXReal, this.centerYReal - this.radiusReal / 2 + this.topTextYOffset);
            this.chart.graphsSet.push(a);
            this.topTF = a
        }
    }
}, setBottomText: function (a) {
    if (void 0 !== a) {
        this.bottomText = a;
        var b = this.chart;
        if (this.axisCreated) {
            this.bottomTF && this.bottomTF.remove();
            var d = this.bottomTextFontSize;
            d || (d = b.fontSize);
            var c = this.bottomTextColor;
            c || (c = b.color);
            a = AmCharts.text(b.container, a, c, b.fontFamily,
                d, void 0, this.bottomTextBold);
            a.translate(this.centerXReal, this.centerYReal + this.radiusReal / 2 + this.bottomTextYOffset);
            this.bottomTF = a;
            this.chart.graphsSet.push(a)
        }
    }
}, draw: function () {
    var a = this.chart, b = a.graphsSet, d = this.startValue, c = this.valueInterval, l = this.startAngle, g = this.endAngle, h = this.tickLength, m = (this.endValue - d) / c + 1, f = (g - l) / (m - 1), q = f / c;
    this.singleValueAngle = q;
    var e = a.container, k = this.tickColor, w = this.tickAlpha, u = this.tickThickness, C = c / this.minorTickInterval, E = f / C, F = this.minorTickLength,
        G = this.labelFrequency, s = this.radiusReal;
    this.inside || (s -= 15);
    var y = a.centerX + AmCharts.toCoordinate(this.centerX, a.realWidth), z = a.centerY + AmCharts.toCoordinate(this.centerY, a.realHeight);
    this.centerXReal = y;
    this.centerYReal = z;
    var H = {fill: this.axisColor, "fill-opacity": this.axisAlpha, "stroke-width": 0, "stroke-opacity": 0}, n, A;
    this.gridInside ? A = n = s : (n = s - h, A = n + F);
    var r = this.axisThickness / 2, g = AmCharts.wedge(e, y, z, l, g - l, n + r, n + r, n - r, 0, H);
    b.push(g);
    g = AmCharts.doNothing;
    AmCharts.isModern || (g = Math.round);
    H = AmCharts.getDecimals(c);
    for (n = 0; n < m; n++) {
        var p = d + n * c, r = l + n * f, v = g(y + s * Math.sin(r / 180 * Math.PI)), B = g(z - s * Math.cos(r / 180 * Math.PI)), x = g(y + (s - h) * Math.sin(r / 180 * Math.PI)), t = g(z - (s - h) * Math.cos(r / 180 * Math.PI)), v = AmCharts.line(e, [v, x], [B, t], k, w, u, 0, !1, !1, !0);
        b.push(v);
        v = -1;
        x = this.labelOffset;
        this.inside || (x = -x - h, v = 1);
        var B = Math.sin(r / 180 * Math.PI), t = Math.cos(r / 180 * Math.PI), B = y + (s - h - x) * B, x = z - (s - h - x) * t, D = this.fontSize;
        isNaN(D) && (D = a.fontSize);
        var t = Math.sin((r - 90) / 180 * Math.PI), J = Math.cos((r - 90) / 180 * Math.PI);
        if (0 < G && n / G == Math.round(n /
            G) && (this.showLastLabel || n != m - 1) && (this.showFirstLabel || 0 !== n)) {
            var p = AmCharts.formatNumber(p, a.numberFormatter, H), I = this.unit;
            I && (p = "left" == this.unitPosition ? I + p : p + I);
            p = AmCharts.text(e, p, a.color, a.fontFamily, D);
            D = p.getBBox();
            p.translate(B + v * D.width / 2 * J, x + v * D.height / 2 * t);
            b.push(p)
        }
        if (n < m - 1)for (p = 1; p < C; p++)t = r + E * p, v = g(y + A * Math.sin(t / 180 * Math.PI)), B = g(z - A * Math.cos(t / 180 * Math.PI)), x = g(y + (A - F) * Math.sin(t / 180 * Math.PI)), t = g(z - (A - F) * Math.cos(t / 180 * Math.PI)), v = AmCharts.line(e, [v, x], [B, t], k, w, u, 0, !1, !1, !0),
            b.push(v)
    }
    if (b = this.bands)for (d = 0; d < b.length; d++)if (c = b[d])k = c.startValue, w = c.endValue, h = AmCharts.toCoordinate(c.radius, s), isNaN(h) && (h = A), m = AmCharts.toCoordinate(c.innerRadius, s), isNaN(m) && (m = h - F), f = l + q * k, w = q * (w - k), u = c.outlineColor, void 0 == u && (u = this.bandOutlineColor), C = c.outlineThickness, isNaN(C) && (C = this.bandOutlineThickness), E = c.outlineAlpha, isNaN(E) && (E = this.bandOutlineAlpha), k = c.alpha, isNaN(k) && (k = this.bandAlpha), c = AmCharts.wedge(e, y, z, f, w, h, h, m, 0, {fill: c.color, stroke: u, "stroke-width": C, "stroke-opacity": E}),
        c.setAttr("opacity", k), a.gridSet.push(c);
    this.axisCreated = !0;
    this.setTopText(this.topText);
    this.setBottomText(this.bottomText);
    a = a.graphsSet.getBBox();
    this.width = a.width;
    this.height = a.height
}});
AmCharts.GaugeArrow = AmCharts.Class({construct: function (a) {
    this.cname = "GaugeArrow";
    this.color = "#000000";
    this.nailAlpha = this.alpha = 1;
    this.startWidth = this.nailRadius = 8;
    this.endWidth = 0;
    this.borderAlpha = 1;
    this.radius = "90%";
    this.nailBorderAlpha = this.innerRadius = 0;
    this.nailBorderThickness = 1;
    this.frame = 0;
    AmCharts.applyTheme(this, a, "GaugeArrow")
}, setValue: function (a) {
    var b = this.chart;
    b ? b.setValue(this, a) : this.previousValue = this.value = a
}});
AmCharts.GaugeBand = AmCharts.Class({construct: function () {
    this.cname = "GaugeBand"
}});
AmCharts.AmAngularGauge = AmCharts.Class({inherits: AmCharts.AmChart, construct: function (a) {
    this.cname = "AmAngularGauge";
    AmCharts.AmAngularGauge.base.construct.call(this, a);
    this.theme = a;
    this.type = "gauge";
    this.minRadius = this.marginRight = this.marginBottom = this.marginTop = this.marginLeft = 10;
    this.faceColor = "#FAFAFA";
    this.faceAlpha = 0;
    this.faceBorderWidth = 1;
    this.faceBorderColor = "#555555";
    this.faceBorderAlpha = 0;
    this.arrows = [];
    this.axes = [];
    this.startDuration = 1;
    this.startEffect = "easeOutSine";
    this.adjustSize = !0;
    this.extraHeight = this.extraWidth = 0;
    AmCharts.applyTheme(this, a, this.cname)
}, addAxis: function (a) {
    this.axes.push(a)
}, formatString: function (a, b) {
    return a = AmCharts.formatValue(a, b, ["value"], this.numberFormatter, "", this.usePrefixes, this.prefixesOfSmallNumbers, this.prefixesOfBigNumbers)
}, initChart: function () {
    AmCharts.AmAngularGauge.base.initChart.call(this);
    var a;
    0 === this.axes.length && (a = new AmCharts.GaugeAxis(this.theme), this.addAxis(a));
    var b;
    for (b = 0; b < this.axes.length; b++)a = this.axes[b], a = AmCharts.processObject(a,
        AmCharts.GaugeAxis, this.theme), a.chart = this, this.axes[b] = a;
    var d = this.arrows;
    for (b = 0; b < d.length; b++) {
        a = d[b];
        a = AmCharts.processObject(a, AmCharts.GaugeArrow, this.theme);
        a.chart = this;
        d[b] = a;
        var c = a.axis;
        AmCharts.isString(c) && (a.axis = AmCharts.getObjById(this.axes, c));
        a.axis || (a.axis = this.axes[0]);
        isNaN(a.value) && a.setValue(a.axis.startValue);
        isNaN(a.previousValue) && (a.previousValue = a.axis.startValue)
    }
    this.setLegendData(d);
    this.drawChart();
    this.totalFrames = 1E3 * this.startDuration / AmCharts.updateRate
}, drawChart: function () {
    AmCharts.AmAngularGauge.base.drawChart.call(this);
    var a = this.container, b = this.updateWidth();
    this.realWidth = b;
    var d = this.updateHeight();
    this.realHeight = d;
    var c = AmCharts.toCoordinate, l = c(this.marginLeft, b), g = c(this.marginRight, b), h = c(this.marginTop, d) + this.getTitleHeight(), m = c(this.marginBottom, d), f = c(this.radius, b, d), c = b - l - g, q = d - h - m + this.extraHeight;
    f || (f = Math.min(c, q) / 2);
    f < this.minRadius && (f = this.minRadius);
    this.radiusReal = f;
    this.centerX = (b - l - g) / 2 + l;
    this.centerY = (d - h - m) / 2 + h + this.extraHeight / 2;
    isNaN(this.gaugeX) || (this.centerX = this.gaugeX);
    isNaN(this.gaugeY) ||
    (this.centerY = this.gaugeY);
    var b = this.faceAlpha, d = this.faceBorderAlpha, e;
    if (0 < b || 0 < d)e = AmCharts.circle(a, f, this.faceColor, b, this.faceBorderWidth, this.faceBorderColor, d, !1), e.translate(this.centerX, this.centerY), e.toBack(), (a = this.facePattern) && e.pattern(a);
    for (b = f = a = 0; b < this.axes.length; b++)d = this.axes[b], d.radiusReal = AmCharts.toCoordinate(d.radius, this.radiusReal), d.draw(), d.width > a && (a = d.width), d.height > f && (f = d.height);
    (b = this.legend) && b.invalidateSize();
    if (this.adjustSize && !this.chartCreated) {
        e &&
        (e = e.getBBox(), e.width > a && (a = e.width), e.height > f && (f = e.height));
        e = 0;
        if (q > f || c > a)e = Math.min(q - f, c - a);
        0 < e && (this.extraHeight = q - f, this.chartCreated = !0, this.validateNow())
    }
    this.dispDUpd();
    this.chartCreated = !0
}, validateSize: function () {
    this.extraHeight = this.extraWidth = 0;
    this.chartCreated = !1;
    AmCharts.AmAngularGauge.base.validateSize.call(this)
}, addArrow: function (a) {
    this.arrows.push(a)
}, removeArrow: function (a) {
    AmCharts.removeFromArray(this.arrows, a);
    this.validateNow()
}, removeAxis: function (a) {
    AmCharts.removeFromArray(this.axes,
        a);
    this.validateNow()
}, drawArrow: function (a, b) {
    a.set && a.set.remove();
    var d = this.container;
    a.set = d.set();
    if (!a.hidden) {
        var c = a.axis, l = c.radiusReal, g = c.centerXReal, h = c.centerYReal, m = a.startWidth, f = a.endWidth, q = AmCharts.toCoordinate(a.innerRadius, c.radiusReal), e = AmCharts.toCoordinate(a.radius, c.radiusReal);
        c.inside || (e -= 15);
        var k = a.nailColor;
        k || (k = a.color);
        var w = a.nailColor;
        w || (w = a.color);
        k = AmCharts.circle(d, a.nailRadius, k, a.nailAlpha, a.nailBorderThickness, k, a.nailBorderAlpha);
        a.set.push(k);
        k.translate(g,
            h);
        isNaN(e) && (e = l - c.tickLength);
        var c = Math.sin(b / 180 * Math.PI), l = Math.cos(b / 180 * Math.PI), k = Math.sin((b + 90) / 180 * Math.PI), u = Math.cos((b + 90) / 180 * Math.PI), d = AmCharts.polygon(d, [g - m / 2 * k + q * c, g + e * c - f / 2 * k, g + e * c + f / 2 * k, g + m / 2 * k + q * c], [h + m / 2 * u - q * l, h - e * l + f / 2 * u, h - e * l - f / 2 * u, h - m / 2 * u - q * l], a.color, a.alpha, 1, w, a.borderAlpha, void 0, !0);
        a.set.push(d);
        this.graphsSet.push(a.set)
    }
}, setValue: function (a, b) {
    a.axis && (a.axis.value2angle(b), a.frame = 0, a.previousValue = a.value);
    a.value = b;
    var d = this.legend;
    d && d.updateValues()
}, handleLegendEvent: function (a) {
    var b =
        a.type;
    a = a.dataItem;
    if (!this.legend.data && a)switch (b) {
        case "hideItem":
            this.hideArrow(a);
            break;
        case "showItem":
            this.showArrow(a)
    }
}, hideArrow: function (a) {
    a.set.hide();
    a.hidden = !0
}, showArrow: function (a) {
    a.set.show();
    a.hidden = !1
}, updateAnimations: function () {
    AmCharts.AmAngularGauge.base.updateAnimations.call(this);
    for (var a = this.arrows.length, b, d = 0; d < a; d++) {
        b = this.arrows[d];
        var c;
        b.frame >= this.totalFrames ? c = b.value : (b.frame++, b.clockWiseOnly && b.value < b.previousValue && (c = b.axis, b.previousValue -= c.endValue -
            c.startValue), c = AmCharts.getEffect(this.startEffect), c = AmCharts[c](0, b.frame, b.previousValue, b.value - b.previousValue, this.totalFrames), isNaN(c) && (c = b.value));
        c = b.axis.value2angle(c);
        this.drawArrow(b, c)
    }
}});