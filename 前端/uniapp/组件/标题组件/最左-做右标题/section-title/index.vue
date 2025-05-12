<script setup lang="ts">
import { ref } from 'vue';

interface Props {
  title?: string;
  rightText?: string;
  rightIcon?: string;
  titleColor?: string;
  rightTextColor?: string;
  rightIconColor?: string;
  titleSize?: string;
  rightSize?: string;
  width?: string;
  height?: string;
}

const props = withDefaults(defineProps<Props>(), {
  title: '每日推荐',
  rightText: '',
  rightIcon: 'calendar',
  titleColor: '#333333',
  rightTextColor: '#44B549',
  rightIconColor: '#44B549',
  titleSize: '36rpx',
  rightSize: '28rpx',
  width: '700rpx',
  height: '42rpx'
});

const emit = defineEmits<{
  (e: 'click'): void;
  (e: 'moreClick'): void;
}>();

const handleClick = () => {
  emit('click');
};

const handleMoreClick = () => {
  emit('moreClick');
};
</script>

<template>
  <view class="section-title" :style="{ width: props.width, height: props.height }" @click="handleClick">
    <!-- 左侧标题 -->
    <view class="title-left">
      <text class="title-text" :style="{ color: props.titleColor, fontSize: props.titleSize }">{{ props.title }}</text>
    </view>
    
    <!-- 右侧内容 -->
    <view class="title-right" @click.stop="handleMoreClick" v-if="props.rightText">
      <uni-icons 
        :type="props.rightIcon" 
        :size="Number(props.rightSize.replace('rpx', ''))/2" 
        :color="props.rightIconColor" 
        class="right-icon"
      ></uni-icons>
      <text class="right-text" :style="{ color: props.rightTextColor, fontSize: props.rightSize }">{{ props.rightText }}</text>
    </view>
  </view>
</template>

<style lang="scss" scoped>
.section-title {
  display: flex;
  align-items: center;
  justify-content: space-between;
  box-sizing: border-box;
  
  .title-left {
    display: flex;
    align-items: center;
    
    .title-text {
      font-weight: 600;
    }
  }
  
  .title-right {
    display: flex;
    align-items: center;
    
    .right-icon {
      margin-right: 4rpx;
    }
  }
}
</style> 