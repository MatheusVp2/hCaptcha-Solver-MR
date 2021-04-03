var hsl = function() {
    "use strict";
    Date.prototype.toISOString || function() {
        function r(r) {
            var t = String(r);
            return 1 === t.length && (t = "0" + t), t
        }
        Date.prototype.toISOString = function() {
            return this.getUTCFullYear() + "-" + r(this.getUTCMonth() + 1) + "-" + r(this.getUTCDate()) + "T" + r(this.getUTCHours()) + ":" + r(this.getUTCMinutes()) + ":" + r(this.getUTCSeconds()) + "." + String((this.getUTCMilliseconds() / 1e3).toFixed(3)).slice(2, 5) + "Z"
        }
    }();
    var r = function(r) {
            try {
                var t = r.split(".");
                return {
                    header: JSON.parse(atob(t[0])),
                    payload: JSON.parse(atob(t[1])),
                    signature: atob(t[2].replace(/_/g, "/").replace(/-/g, "+")),
                    raw: {
                        header: t[0],
                        payload: t[1],
                        signature: t[2]
                    }
                }
            } catch (e) {
                throw new Error("Token is invalid.")
            }
        },
        t = {
            hash: function(r) {
                if ("string" != typeof r) throw new Error("Message Must Be String");
                for (var e = [1518500249, 1859775393, 2400959708, 3395469782], n = [1732584193, 4023233417, 2562383102, 271733878, 3285377520], o = unescape(encodeURIComponent(r)), a = (o += String.fromCharCode(128)).length / 4 + 2, i = Math.ceil(a / 16), s = new Array(i), u = 0; u < i; u++) {
                    s[u] = new Array(16);
                    for (var c = 0; c < 16; c++) s[u][c] = o.charCodeAt(64 * u + 4 * c + 0) << 24 | o.charCodeAt(64 * u + 4 * c + 1) << 16 | o.charCodeAt(64 * u + 4 * c + 2) << 8 | o.charCodeAt(64 * u + 4 * c + 3) << 0
                }
                s[i - 1][14] = 8 * (o.length - 1) / Math.pow(2, 32), s[i - 1][14] = Math.floor(s[i - 1][14]), s[i - 1][15] = 8 * (o.length - 1) & 4294967295;
                for (var f = 0; f < i; f++) {
                    for (var h = new Array(80), l = 0; l < 16; l++) h[l] = s[f][l];
                    for (var g = 16; g < 80; g++) h[g] = t.rotateLeft(h[g - 3] ^ h[g - 8] ^ h[g - 14] ^ h[g - 16], 1);
                    for (var d = n[0], v = n[1], p = n[2], w = n[3], y = n[4], S = 0; S < 80; S++) {
                        var C = Math.floor(S / 20),
                            T = t.rotateLeft(d, 5) + t.f(C, v, p, w) + y + e[C] + h[S] >>> 0;
                        y = w, w = p, p = t.rotateLeft(v, 30) >>> 0, v = d, d = T
                    }
                    n[0] = n[0] + d >>> 0, n[1] = n[1] + v >>> 0, n[2] = n[2] + p >>> 0, n[3] = n[3] + w >>> 0, n[4] = n[4] + y >>> 0
                }
                return n
            },
            digest: function(r) {
                return [r[0] >> 24 & 255, r[0] >> 16 & 255, r[0] >> 8 & 255, 255 & r[0], r[1] >> 24 & 255, r[1] >> 16 & 255, r[1] >> 8 & 255, 255 & r[1], r[2] >> 24 & 255, r[2] >> 16 & 255, r[2] >> 8 & 255, 255 & r[2], r[3] >> 24 & 255, r[3] >> 16 & 255, r[3] >> 8 & 255, 255 & r[3], r[4] >> 24 & 255, r[4] >> 16 & 255, r[4] >> 8 & 255, 255 & r[4]]
            },
            hex: function(r) {
                for (var t = [], e = 0; e < r.length; e++) t.push(("00000000" + r[e].toString(16)).slice(-8));
                return t.join("")
            },
            rotateLeft: function(r, t) {
                return r << t | r >>> 32 - t
            },
            f: function(r, t, e, n) {
                switch (r) {
                    case 0:
                        return t & e ^ ~t & n;
                    case 1:
                        return t ^ e ^ n;
                    case 2:
                        return t & e ^ t & n ^ e & n;
                    case 3:
                        return t ^ e ^ n
                }
            }
        },
        e = "0123456789/:abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ";

    function n(r, t) {
        var e = function(r, t) {
            for (var e = 0; e < 25; e++) {
                for (var n = Array(e), s = 0; s < e; s++) n[s] = 0;
                for (; a(n);) {
                    var u = t + "::" + i(n);
                    if (o(r, u)) return i(n)
                }
            }
        }(r, t);
        return "1:" + r + ":" + (new Date).toISOString().slice(0, 19).replace(/[-:T]/g, "") + ":" + t + "::" + e
    }

    function o(r, e) {
        return function(r, t) {
            var e, n = -1,
                o = [];
            for (; ++n < 8 * t.length;) e = t[Math.floor(n / 8)] >> n % 8 & 1, o.push(e);
            var a = o.slice(0, r);
            return 0 == a[0] && (a.indexOf(1) >= r - 1 || -1 == a.indexOf(1))
        }(r, (n = e, o = t.hash(n), t.digest(o)));
        var n, o
    }

    function a(r) {
        for (var t = r.length - 1; t >= 0; t--) {
            if (r[t] < e.length - 1) return r[t] += 1, !0;
            r[t] = 0
        }
        return !1
    }

    function i(r) {
        for (var t = "", n = 0; n < r.length; n++) t += e[r[n]];
        return t
    }
    var s = new Function("try{return(function(){try{return this===window&&this.document!=='undefined';}catch(e){return false;}}())&&!(function(){try{return this===global||(typeof process!=='undefined'&&process.versions!=null&&process.versions.node!=null);}catch(e){return false;}}())&&!(function(){try{return this===window&&(this.name==='nodejs'||navigator.userAgent.includes('Node.js')||navigator.userAgent.includes('jsdom'))}catch(e){return false;}}())}catch(e){return false;}");
    return function(t) {
        return new Promise((function(e, o) {
            try {
                var a = r(t).payload,
                    i = (s() ? "" : "@") + a.d,
                    u = a.s;
                if (!i || !u) throw new TypeError("Invalid Spec");
                e(n(u, i))
            } catch (c) {
                o(c)
            }
        }))
    }
}();