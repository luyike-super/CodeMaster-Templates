<script setup lang="ts">
import { ref, computed } from 'vue';

interface NoticeItem {
  id: number;
  content: string;
  url?: string;
}

interface Props {
  list: NoticeItem[];
  width?: string;
  height?: string;
  backgroundColor?: string;
  textColor?: string;
  iconColor?: string;
}

const props = withDefaults(defineProps<Props>(), {
  list: () => [],
  width: '698rpx',
  height: '78rpx',
  backgroundColor: '#f9f9f9',
  textColor: '#333333',
  iconColor: '#44B549'
});

const emit = defineEmits<{
  (e: 'click', item: NoticeItem): void;
  (e: 'more'): void;
}>();

const current = ref(0);

const handleChange = (e: any) => {
  current.value = e.detail.current;
};

const handleClick = (item: NoticeItem) => {
  emit('click', item);
};

const handleMore = () => {
  emit('more');
};

// 动态计算圆角大小，取高度的一半
const borderRadius = computed(() => {
  // 从高度字符串中提取数值
  const heightValue = parseInt(props.height);
  // 返回一半高度作为圆角值
  return heightValue ? `${heightValue / 2}rpx` : '39rpx';
});
</script>

<template>
  <view class="notice-container" :style="{ 
      width: props.width, 
      height: props.height,
      borderRadius: borderRadius,
      backgroundColor: props.backgroundColor
    }">
    <!-- 左侧区域 -->
    <view class="notice-left" :style="{ color: props.iconColor }">
      <uni-icons type="sound-filled" size="22" class="sound-icon"></uni-icons>
      <text class="title-text">公告</text>
    </view>
    
    <!-- 中间轮播区域 -->
    <view class="notice-center">
      <swiper
        class="notice-swiper"
        :autoplay="true"
        :interval="3000"
        :circular="true"
        :vertical="true"
        :indicator-dots="false"
        @change="handleChange"
      >
        <swiper-item 
          v-for="item in props.list" 
          :key="item.id" 
          class="swiper-item"
          @click="handleClick(item)"
        >
          <text class="notice-text" :style="{ color: props.textColor }">{{ item.content }}</text>
        </swiper-item>
      </swiper>
    </view>
    
    <!-- 右侧区域 -->
    <view class="notice-right" @click="handleMore" :style="{ color: props.iconColor }">
      <uni-icons type="right" size="22"></uni-icons>
    </view>
  </view>
</template>

<style lang="scss" scoped>
.notice-container {
  display: flex;
  align-items: center;
  overflow: hidden;
  box-sizing: border-box;
  
  .notice-left {
    width: 150rpx;
    display: flex;
    align-items: center;
    justify-content: center;
    
    .title-text {
      font-size: 32rpx;
      font-weight: 500;
      margin-right: 8rpx;
    }
  }
  
  .notice-center {
    flex: 1;
    height: 100%;
    
    .notice-swiper {
      width: 100%;
      height: 100%;
      
      .swiper-item {
        display: flex;
        align-items: center;
        
        .notice-text {
          font-size: 28rpx;
          overflow: hidden;
          text-overflow: ellipsis;
          white-space: nowrap;
        }
      }
    }
  }
  
  .notice-right {
    width: 92rpx;
    display: flex;
    align-items: center;
    justify-content: center;
  }
}
</style> 