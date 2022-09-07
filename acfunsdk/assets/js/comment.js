
let hotList = document.getElementById('comment-hot-list'),
    rootList = document.getElementById('comment-root-list'),
    commentPageNow=1;

function commentBlock(commentItem, subCommentsMap, isTop=false, nohr =false) {
    function pos2time(p) {
        let t = new Date(p);
        return t.toLocaleString("zh-CN");
    }

    let userLink = 'http://www.acfun.cn/u/',
        userPath = '../../member/',
        cid = commentItem.commentId.toString(),
        ncolor = {
            '1': "color: #fd4c5c",
            '2': "color: #964cfd",
            '3': "color: #ff862a"
        },
        itemContent = commentItem.content,
        srcUrl = document.getElementById("srcUrl").getAttribute("href");

    if(commentItem.replyTo!==0){
        itemContent = "回复<a data-uid='"+commentItem.replyTo+"'>@"+commentItem.replyToUserName+"</a>: "+commentItem.content;
    }

    let mainDiv = document.createElement("div"),
        commentMain = document.createElement("div"),
            commentFirst = document.createElement("div"),
                commentFirstLeft = document.createElement("div"),
                    commentAcerAvatarLink = document.createElement("a"),
                        commentAcerAvatarImg = document.createElement("img"),
                commentFirstRight = document.createElement("div"),
                    commentTitle = document.createElement("div"),
                        commentTitleAcerLink = document.createElement("a"),
                        commentTitleText = document.createElement("span"),
                        commentTitleTime = document.createElement("span"),
                    commentDesc = document.createElement("div"),
                        commentDescContent = document.createElement("p"),
                    commentTool = document.createElement("div"),
                        commentToolLike = document.createElement("a"),
                        commentToolReply = document.createElement("a"),
                        commentToolFrom = document.createElement("span"),
                            commentToolFromText = document.createElement("span"),
                            commentToolFromHere = document.createElement("span"),
                        commentToolMore = document.createElement("div"),
                commentFirstIndex = document.createElement("span"),

            commentSec = document.createElement("div"),
                commentArea = document.createElement("div"),
                    commentList = document.createElement("div"),  // 迭代评论块
                    commentPager = document.createElement("div"),
        commentEnd = document.createElement("hr");

        commentMain.setAttribute('class', 'area-comment-top clearfix main-comment-item-'+cid);
        commentMain.setAttribute('data-commentid', cid);
        commentMain.setAttribute('id', 'comment-'+cid);
            commentFirst.setAttribute('class', 'area-comment-first clearfix');
            commentFirst.setAttribute('id', 'comment-first-'+cid);
                commentFirstLeft.setAttribute('class', 'area-comment-left');
                    commentAcerAvatarLink.setAttribute('class', 'thumb');
                    commentAcerAvatarLink.setAttribute('target', '_blank');
                    commentAcerAvatarLink.setAttribute('href', userLink+commentItem.userId.toString());
                        commentAcerAvatarImg.setAttribute('class', 'avatar lazy');
                        commentAcerAvatarImg.setAttribute('alt', commentItem.userId.toString());
                        commentAcerAvatarImg.setAttribute('src', "../../assets/img/defaultAvatar.jpg");
                        commentAcerAvatarImg.setAttribute('data-src', userPath+commentItem.userId.toString()+'_avatar');
                        commentAcerAvatarImg.setAttribute('onerror', "javascript:this.src='../../assets/img/defaultAvatar.jpg';")

                    commentAcerAvatarLink.appendChild(commentAcerAvatarImg);
                commentFirstLeft.appendChild(commentAcerAvatarLink);

                commentFirstRight.setAttribute('class', 'area-comment-right');
                    commentTitle.setAttribute('class', 'area-comment-title');
                    commentTitle.setAttribute('title', commentItem.commentId.toString());
                        commentTitleAcerLink.setAttribute('class', 'name');
                        commentTitleAcerLink.setAttribute('target', '_blank');
                        commentTitleAcerLink.setAttribute('href', userLink+commentItem.userId.toString());
                        commentTitleAcerLink.setAttribute('data-userid', commentItem.userId.toString());
                        commentTitleAcerLink.innerHTML = commentItem.userName;
                        if(commentItem.nameColor!==0){
                            commentTitleAcerLink.setAttribute('style', ncolor[commentItem.nameColor.toString()]);
                        }

                        commentTitleText.setAttribute('class', 'time_day');
                        commentTitleText.innerHTML = "发表于";
                        commentTitleTime.setAttribute('class', 'time_times');
                        commentTitleTime.innerHTML = pos2time(commentItem.timestamp);

                    commentTitle.appendChild(commentTitleAcerLink);
                    commentTitle.appendChild(commentTitleText);
                    commentTitle.appendChild(commentTitleTime);

                    commentDesc.setAttribute('class', 'area-comment-des');
                        commentDescContent.setAttribute('class', 'area-comment-des-content');
                        commentDescContent.innerHTML = itemContent;
                    commentDesc.appendChild(commentDescContent);

                    commentTool.setAttribute('class', 'area-comment-tool');
                        commentToolLike.setAttribute('class', 'area-comment-like area-comment-up');
                        commentToolLike.innerHTML = "赞"+(parseInt(commentItem.likeCount)>0?commentItem.likeCountFormat:"");
                        commentToolLike.setAttribute('target', '_blank');
                        commentToolLike.href = srcUrl+"#ncid="+commentItem.commentId;

                        commentToolReply.setAttribute('class', 'area-comment-reply');
                        commentToolReply.innerHTML = "回复";
                        commentToolReply.setAttribute('target', '_blank');
                        commentToolReply.href = srcUrl+"#ncid="+commentItem.commentId;

                        commentToolFrom.setAttribute('class', 'area-comment-from');
                            commentToolFromText.innerHTML = "来自";
                            commentToolFromHere.setAttribute('style', 'margin-left:3px;');
                            commentToolFromHere.innerHTML = commentItem.deviceModel;
                        commentToolFrom.appendChild(commentToolFromText);
                        commentToolFrom.appendChild(commentToolFromHere);
                        commentToolMore.setAttribute('class', 'area-comment-more');
                    commentTool.appendChild(commentToolLike);
                    commentTool.appendChild(commentToolReply);
                    commentTool.appendChild(commentToolFrom);
                    commentTool.appendChild(commentToolMore);
                commentFirstRight.appendChild(commentTitle);
                commentFirstRight.appendChild(commentDesc);
                commentFirstRight.appendChild(commentTool);

                commentFirstIndex.setAttribute('class', 'index-comment');
                commentFirstIndex.innerHTML = "#"+commentItem.floor.toString();

            commentFirst.appendChild(commentFirstLeft);
            commentFirst.appendChild(commentFirstRight);
            if(isTop){
                commentFirst.appendChild(commentFirstIndex);
            }

            commentSec.setAttribute('id', 'comment-sec-'+cid);
                commentArea.setAttribute('class', 'area-comment-sec area-sec-close clearfix');
                    commentList.setAttribute('class', 'area-sec-list');
                    commentList.setAttribute('id', 'area-sec-list-'+cid);

                commentPager.setAttribute('id', 'area-sec-pager-'+cid);
                commentArea.appendChild(commentList);
                commentArea.appendChild(commentPager);
            commentSec.appendChild(commentArea);
        commentMain.appendChild(commentFirst);
        commentMain.appendChild(commentSec);
        if(nohr==false){
            commentMain.appendChild(commentEnd);
        }
    mainDiv.appendChild(commentMain);

    // 循环插入 commentBlock
    if(subCommentsMap.hasOwnProperty(cid)){
        subCommentsMap[cid]['subComments'].forEach(function (item, index) {
            commentList.appendChild(commentBlock(item, {}));
        });
    }else{
        commentSec.innerHTML = "";
    }
    return mainDiv;
}

function commentPager(curPage, total) {
    if(total==1){return false;}
    function pageBtn(n) {
        let p = document.createElement('a');
        p.setAttribute('class', 'pager__btn');
        p.innerHTML = n;
        p.addEventListener('click', function () {
            loadComments(parseInt(p.innerHTML));
        });
        return p;
    }
    let pageMain = document.createElement('div'),
        pageWrapper = document.createElement('div'),
        pagePrev = document.createElement('a'),
        pageNext = document.createElement('a'),
        pageFirst = document.createElement('a'),
        pageEnd = document.createElement('a'),
        pageInputDiv = document.createElement('div'),
        pageInput = document.createElement('input'),
        pageTags = [];
    pageMain.setAttribute('id', 'page-main');
    pageWrapper.setAttribute('class', 'pager__wrapper');
    pagePrev.innerHTML = "上一页";
    if(curPage>1){
        pagePrev.setAttribute('class', 'pager__btn pager__btn__prev');
        pagePrev.addEventListener('click', function () {loadComments(curPage-1);});
    }else{
        pagePrev.setAttribute('class', 'pager__btn pager__btn__prev pager__btn__disabled');
    }
    pageNext.innerHTML = "下一页";
    if(curPage<total){
        pageNext.setAttribute('class', 'pager__btn pager__btn__next');
        pageNext.addEventListener('click', function () {loadComments(curPage+1);});
    }else{
        pageNext.setAttribute('class', 'pager__btn pager__btn__next pager__btn__disabled');
    }
    pageFirst.setAttribute('class', 'pager__btn');
    pageFirst.innerHTML = "1";
    pageEnd.setAttribute('class', 'pager__btn');
    pageInputDiv.setAttribute('class', 'pager__input');
    pageInputDiv.append("跳至");
    pageInput.setAttribute('type', 'text');
    pageInput.addEventListener('keydown', function (ev) {
        if (ev.key == 'Enter') {
            let i = parseInt(pageInput.value);
            if (i == NaN || 1 > i > total || i == commentPageNow) {
                return false;
            } else {
                loadComments(i);
            }
        }
    })
    pageInputDiv.append(pageInput);
    pageInputDiv.append("页");
    pageTags.push(pagePrev);
    let cMax = 3,
        cLeft = curPage - cMax, cRight = curPage + cMax,
        pStart = cLeft < 1 ? 1 : cLeft, pEnd = cRight > total ? total : cRight;
    for (let i = pStart; i <= pEnd; i++) {
        // console.log(i);
        let nPage = pageBtn(i);
        if(i == curPage) { // 当前页
            nPage.setAttribute('class', 'pager__btn pager__btn__selected');
            pageTags.push(nPage);
        }else if(curPage - i == cMax){ // 第一个
            if(i != 1){
                let ellipsis = document.createElement('span');
                ellipsis.setAttribute('class', 'pager__ellipsis');
                ellipsis.innerHTML = "...";
                nPage.innerHTML = "1";
                pageTags.push(nPage);
                pageTags.push(ellipsis);
            }else{
                pageTags.push(nPage);
            }
        }else if(i - curPage == cMax){ // 最后一个
            if(i != total){
                let ellipsis = document.createElement('span');
                ellipsis.setAttribute('class', 'pager__ellipsis');
                ellipsis.innerHTML = "...";
                nPage.innerHTML = total.toString();
                pageTags.push(ellipsis);
                pageTags.push(nPage);
            }else{
                pageTags.push(nPage);
            }
        }else if(Math.abs(curPage - i) < cMax){ // 其他页
            pageTags.push(nPage);
        }
    }
    pageTags.push(pageNext);
    pageTags.push(pageInputDiv);
    pageTags.forEach(function (item) {
        pageWrapper.append(item);
    });
    pageMain.append(pageWrapper);
    let pager = document.querySelector('.ac-comment-top-pager');
    pager.innerHTML = "";
    pager.append(pageMain);
}

function loadComments(pageNum) {
    let cData = commentData[pageNum];
    if(cData==undefined){
        let src = "data/" + sourceId + ".comment." + pageNum + ".js";
        loadJs(src, function () {loadComments(pageNum);});
        return false
    }
    commentPageNow=pageNum;
    hotList.innerHTML = "";rootList.innerHTML = "";
    let totalToolbar = document.querySelector('#to-comm>.pts'),
        totalText = totalToolbar.innerHTML,
        total = parseInt(totalText);
    document.querySelector(".area-comm-number").innerHTML =
        commentCount + "(总) / "+
        cData.totalComment.toString()+"(存) / "+
        (total - cData.totalComment).toString()+"(删)";
    cData.hotComments.forEach(function (item, index) {
        hotList.appendChild(commentBlock(item, cData.subCommentsMap, true, index==(cData.hotComments.length-1)));
    });
    if(cData.hotComments.length>0){
        hotList.innerHTML += "<div><div class=\"hot-comment-divid\"><hr><span>以上为热门评论</span><hr></div></div>";
    }
    cData.rootComments.forEach(function (item, index) {
        rootList.appendChild(commentBlock(item, cData.subCommentsMap, true));
    });
    commentPager(cData.page, cData.total);
    let lastP = document.getElementById('comment-lastPage'),
        nextP = document.getElementById('comment-nextPage');
    lastP.addEventListener('click', function () {
        if(pageNum>1){loadComments(pageNum-1);}
    });
    nextP.addEventListener('click', function () {
        if(pageNum<cData.total){loadComments(pageNum+1);}
    });
    if(cData.total<=1){
        lastP.style.display = "none";
        nextP.style.display = "none";
    }else{
        if(pageNum==1){
            lastP.style.display = "none";
            nextP.style.display = "";
        }else if(pageNum==cData.total){
            lastP.style.display = "";
            nextP.style.display = "none";
        }else{
            lastP.style.display = "";
            nextP.style.display = "";
        }
    }
    lazyLoadInstance.update();
}

window.onload = function () {
    loadComments(1);
}
