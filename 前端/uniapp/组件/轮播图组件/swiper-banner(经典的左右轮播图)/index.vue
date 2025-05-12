<script setup lang="ts">
import { ref } from 'vue';

interface SwiperItem {
  id: number;
  image: string;
  url?: string;
}

interface Props {
  list: SwiperItem[];
  width?: string;
  height?: string;
  autoplay?: boolean;
  interval?: number;
  duration?: number;
  circular?: boolean;
  indicatorDots?: boolean;
  indicatorColor?: string;
  indicatorActiveColor?: string;
}

const props = withDefaults(defineProps<Props>(), {
  list: () => [],
  width: '700rpx',
  height: '342rpx',
  autoplay: true,
  interval: 3000,
  duration: 500,
  circular: true,
  indicatorDots: true,
  indicatorColor: 'rgba(255, 255, 255, 0.6)',
  indicatorActiveColor: '#ffffff'
});

const emit = defineEmits<{
  (e: 'click', item: SwiperItem): void
}>();

const current = ref(0);

const handleChange = (e: any) => {
  current.value = e.detail.current;
};

const handleClick = (item: SwiperItem) => {
  emit('click', item);
};
</script>

<template>
  <view class="swiper-container" :style="{ width: props.width, height: props.height }">
    <swiper
      class="swiper"
      :autoplay="props.autoplay"
      :interval="props.interval"
      :duration="props.duration"
      :circular="props.circular"
      :indicator-dots="props.indicatorDots"
      :indicator-color="props.indicatorColor"
      :indicator-active-color="props.indicatorActiveColor"
      @change="handleChange"
    >
      <swiper-item v-for="item in props.list" :key="item.id" @click="handleClick(item)">
        <image :src="item.image" mode="aspectFill" class="swiper-image" />
      </swiper-item>
    </swiper>
  </view>
</template>

<style lang="scss" scoped>
.swiper-container {
  border-radius: 12rpx;
  overflow: hidden;
  margin: 0 auto;
  
  .swiper {
    width: 100%;
    height: 100%;
    
    .swiper-image {
      width: 100%;
      height: 100%;
    }
  }
}
</style> 