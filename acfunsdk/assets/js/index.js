let rlistTitle = "" +
    "<div class=\"rlist__banner\">\n" +
    "<div class=\"rlist__title rlist__title--rank\"><p class=\"rlist__text--cn\">内容</p><p class=\"rlist__text--en\">Shows</p></div>\n" +
    "<div class=\"rlist__title rist__title--author\"><p class=\"rlist__text--cn\">Up主</p><p class=\"rlist__text--en\">Author</p></div>\n" +
    "</div>";
let theList = {
    'dom': document.getElementById('ac-list'),
    'cleanup': function () {this.dom.innerHTML = rlistTitle;},
    'addCard': function (data) {
        let basePath = data[0] + "/" + data[1],
            dataJs = basePath + "/data/" + data[1] + ".js",
            thisData;
        function iconText(main_class, sp_class, icon_class, icon_text, text) {
            let sub = document.createElement('span'),
                sp = document.createElement('span'),
                icon = document.createElement('i');
            icon.setAttribute('class', icon_class);
            icon.innerHTML = icon_text || "iconfont";
            sp.append(icon);
            sp.setAttribute('class', sp_class || "icon ac-icon");
            sub.append(sp);
            sub.setAttribute('class', main_class || "");
            sub.append(text);
            return sub;
        }
        loadJs(dataJs, function () {
            if(data[0]=='article'){
                thisData = articles[data[1]];
            }else if(data[0]=='video'){
                thisData = videos[data[1]];
            }
        // console.log(thisData);
        let cell = document.createElement('div'),
            leftC = document.createElement('div'),
            leftLink = document.createElement('a'),
            leftImg = document.createElement('img'),
            playIcon = document.createElement('span'),
            leftInfo = document.createElement('div'),
            leftTitle = document.createElement('a'),
            description = document.createElement('div'),
            leftExtra = document.createElement('div'),
            rightC = document.createElement('div'),
            rightLink = document.createElement('a'),
            rightImg = document.createElement('img'),
            rightInfo = document.createElement('div'),
            upLink = document.createElement('a'),
            upSign = document.createElement('p'),
            upInfo = document.createElement('div');
        if(data[0]=='article'){
            playIcon.innerHTML = "<i class=\"iconfont\"></i>";
        }else{
            playIcon.innerHTML = "<i class=\"iconfont\"></i>";
        }
        playIcon.setAttribute('class', 'play-hover ac-icon');
        leftImg.setAttribute('class', 'preview');
        leftImg.setAttribute('src', basePath + "/cover._");
        leftLink.append(leftImg);
        leftLink.append(playIcon);
        leftLink.setAttribute('class', 'video-card__img');
        leftLink.setAttribute('target', '_Blank');
        leftLink.setAttribute('href', basePath + "/" + data[1] + ".html");
        leftTitle.innerHTML = thisData.title;
        leftTitle.setAttribute('class', 'title');
        leftTitle.setAttribute('target', '_Blank');
        leftTitle.setAttribute('href', basePath + "/" + data[1] + ".html");
        description.innerHTML = thisData.description || "";
        description.setAttribute('class', 'description');
        // 发布时间
        leftExtra.append(iconText('pts', 'icon shallow-gray ac-icon',
            'iconfont', '', thisData.createTime));
        // 浏览量
        leftExtra.append(iconText('pts', 'icon ac-icon',
            'iconfont', data[0]=='article'?'':'', thisData.viewCountShow || thisData.formatViewCount));
        // 评论数量
        leftExtra.append(iconText('pts shallow-gray', 'icon ac-icon',
            'iconfont', '', thisData.formatCommentCount || thisData.commentCountShow));
        if(data[0]=='article'){
            // 收藏数量
            leftExtra.append(iconText('pts shallow-gray', 'icon ac-icon',
                'iconfont', '', thisData.formatStowCount || ""));
        }else {
            // 弹幕数量
            leftExtra.append(iconText('pts shallow-gray', 'icon ac-icon',
                'iconfont', '', thisData.danmakuCountShow || ""));
        }
        let channelText=thisData.channel.name;
        if(data[0]=='article'){
            channelText = thisData.realm.realmName + " / " + channelText;
        }else {
            channelText += " / " + thisData.channel.parentName;
        }
        // 频道名
        leftExtra.append(iconText('pts', 'icon ac-icon', 'iconfont', '', channelText));
        leftExtra.setAttribute('class', 'extra');
        leftInfo.innerHTML = "<span class=\"number\">"+(document.querySelectorAll('.rlist__cards').length+1)+"</span>";
        leftInfo.append(leftTitle);
        leftInfo.append(description);
        leftInfo.append(leftExtra);
        leftInfo.setAttribute('class', 'video-card__info');
        leftC.append(leftLink);
        leftC.append(leftInfo);
        leftC.setAttribute('class', 'video-card');
        cell.append(leftC);

        rightImg.setAttribute('class', 'avatar');
        rightImg.setAttribute('src', 'member/' + thisData.user.id + "_avatar");
        rightImg.setAttribute('onerror', "javascript:this.src='assets/img/defaultAvatar.jpg';")
        rightLink.append(rightImg);
        rightLink.setAttribute('class', 'up-card__avatar');
        rightLink.setAttribute('target', '_Blank');
        rightLink.setAttribute('href', 'https://www.acfun.cn/u/' + thisData.user.id);
        upLink.setAttribute('class', 'name');
        upLink.setAttribute('target', '_Blank');
        upLink.setAttribute('href', 'https://www.acfun.cn/u/' + thisData.user.id);
        upLink.innerHTML = thisData.user.name;
        upSign.setAttribute('class', 'sign');
        upSign.innerHTML = thisData.user.signature || thisData.user.verifiedText || thisData.user.comeFrom;
        upInfo.append(iconText('pts', 'icon ac-icon',
            'iconfont', '', thisData.user.followingCount));
        upInfo.append(iconText('pts', 'icon ac-icon',
            'iconfont', '', thisData.user.fanCount));
        upInfo.setAttribute('class', 'extra');
        rightInfo.append(upLink);
        rightInfo.append(upSign);
        rightInfo.append(upInfo);
        rightInfo.setAttribute('class', 'up-card__info');
        rightC.append(rightLink);
        rightC.append(rightInfo);
        rightC.setAttribute('class', 'up-card');
        cell.append(rightC);
        cell.setAttribute('class', 'rlist__cards');
        theList.dom.append(cell);
        });
    }
};

AcCacheList.reverse().forEach(function (item) {
    theList.addCard(item);
});
