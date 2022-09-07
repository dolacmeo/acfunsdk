let danmaku_list = document.getElementById('danmaku-items');
function gen_danmaku_item(danmaku_single) {
    function pos2time(p) {
        let t = new Date(0,0,0,0,0, 0,p);
        return t.toLocaleTimeString();
    }
    var danmaku_li = document.createElement("li"),
        dan_time = document.createElement("div"),
        dan_content = document.createElement("div"),
        dan_user = document.createElement("div");
    danmaku_li.setAttribute('class', 'danmaku-item');
    danmaku_li.setAttribute('data-id', danmaku_single.danmakuId);
    danmaku_li.setAttribute('data-user', danmaku_single.userId);
    danmaku_li.setAttribute('data-time', (danmaku_single.position / 1000).toString());
    danmaku_li.setAttribute('data-message', danmaku_single.body);
    danmaku_li.addEventListener('click', function () {
        document.getElementById('localPlayer').currentTime = (danmaku_single.position / 1000).toString();
    });

    dan_time.setAttribute('class', 'danmaku-time');
    dan_time.innerHTML = pos2time(danmaku_single.position);
    dan_content.setAttribute('class', 'danmaku-content');
    dan_content.innerHTML = danmaku_single.body;
    dan_user.setAttribute('class', 'searchListUser');
    dan_user.setAttribute('style', 'margin-right: 6px; font-size: 20px;');
    dan_user.setAttribute('title', 'UID:' + danmaku_single.userId);
    dan_user.innerHTML = "⌂";
    
    danmaku_li.appendChild(dan_time);
    danmaku_li.appendChild(dan_content);
    danmaku_li.appendChild(dan_user);
    return danmaku_li
}
danmakuData.forEach(function (item, index) {
    danmaku_list.appendChild(gen_danmaku_item(item));
})
document.getElementById('page-info').innerHTML = "共"+danmakuData.length+"条";
