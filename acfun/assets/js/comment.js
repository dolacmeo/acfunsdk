
let hotList = document.getElementById('comment-hot-list'),
    rootList = document.getElementById('comment-root-list');

function commentBlock(commentItem, subCommentsMap, isTop=false) {
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
                        commentAcerAvatarImg.setAttribute('class', 'avatar');
                        commentAcerAvatarImg.setAttribute('src', userPath+commentItem.userId.toString()+'_avatar');
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
                        commentToolLike.innerHTML = "赞"+commentItem.likeCount?"":commentItem.likeCountFormat;
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
        commentMain.appendChild(commentEnd);
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

function loadComments(commentData) {
    let totalToolbar = document.querySelector('#to-comm>.pts'),
        totalText = totalToolbar.innerHTML,
        total = parseInt(totalText);
    document.querySelector(".area-comm-number").innerHTML +=
        "(总) / "+
        commentData.rootComments.length.toString()+"(存) / "+
        (total - commentData.rootComments.length).toString()+"(删)";
    totalToolbar.innerHTML = commentData.rootComments.length.toString();
    commentData.hotComments.forEach(function (item, index) {
        hotList.appendChild(commentBlock(item, commentData.subCommentsMap, true));
    });
    commentData.rootComments.forEach(function (item, index) {
        rootList.appendChild(commentBlock(item, commentData.subCommentsMap, true));
    });
}

window.onload = function () {
    loadComments(commentData);
}
