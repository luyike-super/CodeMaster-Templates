
<!-- 每日推荐图片 -->
<view class="recommend-section">
    <ImageSwiper
        :list="recommendList"
        :autoplay="false"
        :display-multiple-items="2.5"
        previousMargin="0rpx"
        nextMargin="60rpx"
        :circular="false"
        :snap-to-edge="true"
        @click="handleRecommendClick"
    />
</view>

// 每日推荐数据
const recommendList = [
	{
		id: 1,
		image: '/common/images/recommend1.jpg',
		url: '/pages/detail/index'
	},
	{
		id: 2,
		image: '/common/images/recommend2.jpg',
		url: '/pages/detail/index'
	},
	{
		id: 3,
		image: '/common/images/recommend3.jpg',
		url: '/pages/detail/index'
	},
	{
		id: 4,
		image: '/common/images/recommend4.jpg',
		url: '/pages/detail/index'
	}
];