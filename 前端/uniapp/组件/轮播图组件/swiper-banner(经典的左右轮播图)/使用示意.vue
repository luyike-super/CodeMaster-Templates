<template>
	<view class="container">
		<view class="banner-section">
			<SwiperBanner 
				:list="bannerList" 
				width="700rpx" 
				height="342rpx"
				:autoplay="true"
				:interval="3000"
				:circular="true"
				:indicator-dots="true"
				indicator-color="rgba(255, 255, 255, 0.6)"
				indicator-active-color="#FF5500"
				@click="handleBannerClick"
			/>
		</view>
	</view>
</template>

<script setup lang="ts">
import SwiperBanner from '@/components/swiper-banner/index.vue';

// 示例轮播图数据
const bannerList = [
	{
		id: 1,
		image: '/common/images/banner1.jpg',
		url: '/pages/detail/index'
	},
	{
		id: 2,
		image: '/common/images/banner2.jpg',
		url: '/pages/detail/index'
	},
	{
		id: 3,
		image: '/common/images/banner3.jpg',
		url: '/pages/detail/index'
	}
];

// 点击轮播图项
const handleBannerClick = (item: any) => {
	console.log('点击了轮播图项:', item);
	if (item.url) {
		uni.navigateTo({
			url: item.url
		});
	}
};
</script>

<style lang="scss" scoped>
.container {
	padding: 20rpx;
	
	.banner-section {
		display: flex;
		justify-content: center;
		margin-bottom: 30rpx;
	}
}
</style>
