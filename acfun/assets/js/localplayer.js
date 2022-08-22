
let player = document.getElementById('localPlayer'),
    player_logo = document.getElementsByClassName('video-status')[0];
player.addEventListener('play', function (ev) {
    player_logo.setAttribute('data-bind-attr', "play");
});
player.addEventListener('pause', function (ev) {
    player_logo.setAttribute('data-bind-attr', "pause");
});
player.addEventListener('resize', function (ev) {
    var e = this;
    var i = this.lastWindowWidth
      , t = this.lastWindowHeight
      , n = window.innerHeight
      , a = window.innerWidth
      , o = !(a === i)
      , r = !(n === t);
    this.lastWindowWidth = a,
    this.lastWindowHeight = n;
    var l = document.getElementById("main-content")
      , d = document.querySelector(".left-column");
    if (o && !e && !r)
        return a > 1050 && a < 1710 && a <= l.offsetWidth + 100 ? (l.style.maxWidth = 16 * (n - 60 - 90 - 20 - 40) / 9 + 370 + "px",
        l.style.margin = "0 auto") : (l.style.maxWidth = "",
        l.style.margin = "0 auto"),
        l.style.width = "",
        d.style.width = "";
        // void this.handleTitleDescSize();
    if (r || e) {
        var s = n - 60 - 90 - 20 - 40;
        if (n && window.innerWidth > 1150) {
            var c = a - 370 - 100;
            if ((s = s < 382.5 ? 382.5 : s) > 9 * (c = c > 1340 ? 1340 : c) / 16)
                return l.style.width = "",
                l.style.margin = "",
                l.style.maxWidth = c + 370 + "px",
                d.style.width = "";
                // void this.handleTitleDescSize();
            var u = Math.floor(16 * s / 9);
            l.style.width = u + 370 + "px",
            l.style.maxWidth = "",
            l.style.margin = "0 auto",
            d.style.maxWidth = "",
            d.style.width = u + "px"
        } else
            l.style.width = "",
            l.style.maxWidth = "",
            l.style.margin = "",
            d.style.width = "",
            d.style.maxWidth = ""
    }
    // this.handleTitleDescSize()
});
function quickJump(sec) {player.currentTime = sec;goTo("ACPlayer")}
