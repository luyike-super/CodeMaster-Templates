// 公告点击
const handleNoticeClick = (item: any) => {
	console.log('点击了公告:', item);
	if (item.url) {
		uni.navigateTo({
			url: item.url
		});
	}
};

// 公告更多
const handleNoticeMore = () => {
	console.log('查看更多公告');
	uni.navigateTo({
		url: '/pages/notice/list'
	});
};

// 公告数据
const noticeList = [
	{
		id: 1,
		content: '欢迎关注咸虾米圈子公众号，获取更多精彩内容',
		url: '/pages/notice/detail'
	},
	{
		id: 2,
		content: '新功能上线，全新体验等你来发现',
		url: '/pages/notice/detail'
	},
	{
		id: 3,
		content: '618活动开始啦，快来参与抢优惠',
		url: '/pages/notice/detail'
	}
];