<template>
  <view class="image-swiper-container">
    <swiper 
      class="swiper" 
      :circular="circular" 
      :autoplay="autoplay" 
      :interval="interval" 
      :duration="duration"
      @change="handleChange"
      :previous-margin="previousMargin"
      :next-margin="nextMargin"
      :display-multiple-items="displayMultipleItems"
      :snap-to-edge="snapToEdge"
    >
      <swiper-item v-for="(item, index) in list" :key="index" class="swiper-item">
        <view class="swiper-item-wrapper" :class="{ active: current === index }">
          <image 
            :src="item.image" 
            class="swiper-image" 
            mode="aspectFill" 
            @tap="handleItemClick(item)"
          />
        </view>
      </swiper-item>
    </swiper>
  </view>
</template>

<script setup lang="ts">
import { ref, defineProps, defineEmits } from 'vue';

// 定义组件属性
const props = defineProps({
  // 轮播图数据列表
  list: {
    type: Array,
    default: () => []
  },
  // 是否自动播放
  autoplay: {
    type: Boolean,
    default: false
  },
  // 自动播放间隔时间（毫秒）
  interval: {
    type: Number,
    default: 3000
  },
  // 滑动动画时长（毫秒）
  duration: {
    type: Number,
    default: 500
  },
  // 是否循环播放
  circular: {
    type: Boolean,
    default: false
  },
  // 是否显示指示点（默认改为false）
  indicatorDots: {
    type: Boolean,
    default: false
  },
  // 显示多少个item
  displayMultipleItems: {
    type: Number,
    default: 2.5
  },
  // 左边的边距
  previousMargin: {
    type: String,
    default: '0rpx'
  },
  // 右边的边距
  nextMargin: {
    type: String,
    default: '60rpx'
  },
  // 是否贴近边缘
  snapToEdge: {
    type: Boolean,
    default: true
  }
});

// 定义事件
const emit = defineEmits(['click']);

// 当前激活的轮播项索引
const current = ref(0);

// 处理轮播图变化
const handleChange = (e: any) => {
  current.value = e.detail.current;
};

// 处理点击轮播图项
const handleItemClick = (item: any) => {
  emit('click', item);
};
</script>

<style lang="scss" scoped>
.image-swiper-container {
  position: relative;
  width: 100%;
  padding: 0;
  
  .swiper {
    width: 100%;
    height: 442rpx;
  }
  
  .swiper-item {
    display: flex;
    justify-content: center;
    align-items: center;
    box-sizing: border-box;
    
    .swiper-item-wrapper {
      width: 200rpx;
      height: 442rpx;
      overflow: hidden;
      border-radius: 12rpx;
      box-shadow: 0 4rpx 12rpx rgba(0, 0, 0, 0.1);
      margin: 0 7.5rpx; /* 确保图片之间的间隙为15rpx（每边7.5rpx） */
      
      &.active {
        /* 移除了缩放效果 */
      }
    }
    
    .swiper-image {
      width: 100%;
      height: 100%;
      border-radius: 12rpx;
    }
  }
}
</style> 