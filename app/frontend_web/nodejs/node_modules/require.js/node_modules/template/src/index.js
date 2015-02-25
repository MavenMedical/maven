function template(text, data, settings) {
    var render,
        escapes = template.escapes,
        escaper = template.escaper,
        templateSettings = template.settings,

        start, end, match = "([\\s\\S]+?)",
        evaluate, interpolate, escape,

        index = 0,
        source = "__p+='";

    settings || (settings = {});
    for (var key in templateSettings)
        if (settings[key] == null) settings[key] = templateSettings[key];
    start = settings.start;
    end = settings.end;

    evaluate = start + match + end;
    interpolate = start + "=" + match + end;
    escape = start + "-" + match + end;

    text.replace(
        new RegExp(escape + "|" + interpolate + "|" + evaluate + "|$", "g"),
        function(match, escape, interpolate, evaluate, offset) {
            source += text.slice(index, offset).replace(escaper, function(match) {
                return '\\' + escapes[match];
            });

            if (escape) source += "'+\n((__t=(" + escape + "))==null?'':escape(__t))+\n'";
            if (interpolate) source += "'+\n((__t=(" + interpolate + "))==null?'':__t)+\n'";
            if (evaluate) source += "';\n" + evaluate + "\n__p+='";

            index = offset + match.length;

            return match;
        }
    );
    source += "';\n";

    if (!settings.variable) source = 'with(obj||{}){\n' + source + '}\n';
    source = "var __t,__p='',__j=Array.prototype.join, print=function(){__p+=__j.call(arguments,'');};\n" + source + "return __p;\n";

    try {
        render = new Function(settings.variable || 'obj', source);
    } catch (e) {
        e.source = source;
        throw e;
    }
    if (data) return render(data);

    function temp(data) {
        return render.call(this, data);
    }
    temp.source = 'function(' + (settings.variable || 'obj') + '){\n' + source + '}';

    return temp;
}

template.escaper = /\\|'|\r|\n|\t|\u2028|\u2029/g;

template.settings = {
    start: "<%",
    end: "%>",
    interpolate: "=",
    escape: "-"
};

template.escapes = {
    "'": "'",
    "\\": "\\",
    "\r": "r",
    "\n": "n",
    "\t": "t",
    "\u2028": "u2028",
    "\u2029": "u2029"
};


module.exports = template;
