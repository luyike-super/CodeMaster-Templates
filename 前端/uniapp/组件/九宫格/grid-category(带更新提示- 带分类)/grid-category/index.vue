<template>
  <view class="grid-container">
    <view 
      v-for="(item, index) in list" 
      :key="index" 
      class="grid-item"
      @click="handleItemClick(item)"
    >
      <image class="grid-image" :src="item.image" mode="aspectFill"></image>
      <view class="grid-tag">{{ item.updateTime }}</view>
      <view class="grid-title" v-if="index !== list.length - 1 || !lastItemMore">
        {{ item.title }}
      </view>
      <view class="grid-more-dots" v-if="index === list.length - 1 && lastItemMore">
        <text>•••</text>
      </view>
    </view>
  </view>
</template>

<script setup lang="ts">
interface CategoryItem {
  id: number;
  title: string;
  image: string;
  updateTime: string;
  url?: string;
}

const props = defineProps({
  list: {
    type: Array as () => CategoryItem[],
    default: () => []
  },
  // 是否最后一个为"更多"项
  lastItemMore: {
    type: Boolean,
    default: true
  }
});

const emits = defineEmits(['click']);

const handleItemClick = (item: CategoryItem) => {
  emits('click', item);
};
</script>

<style lang="scss" scoped>
.grid-container {
  width: 700rpx;
  height: 1052rpx;
  display: flex;
  flex-wrap: wrap;
  justify-content: space-between;
  align-content: space-between;
}

.grid-item {
  width: 220rpx;
  height: 342rpx;
  position: relative;
  border-radius: 12rpx;
  overflow: hidden;
  box-shadow: 0 4rpx 8rpx rgba(0, 0, 0, 0.1);
}

.grid-image {
  width: 100%;
  height: 100%;
  object-fit: cover;
}

.grid-tag {
  position: absolute;
  top: 10rpx;
  left: 10rpx;
  padding: 4rpx 10rpx;
  background-color: rgba(255, 153, 102, 0.8);
  border-radius: 8rpx;
  color: #ffffff;
  font-size: 20rpx;
  z-index: 1;
}

.grid-title {
  position: absolute;
  bottom: 0;
  left: 0;
  width: 100%;
  padding: 10rpx 0;
  text-align: center;
  background-color: rgba(0, 0, 0, 0.5);
  color: #ffffff;
  font-size: 28rpx;
}

.grid-more-dots {
  position: absolute;
  top: 50%;
  left: 50%;
  transform: translate(-50%, -50%);
  color: #ffffff;
  font-size: 50rpx;
  font-weight: bold;
  text-align: center;
}
</style> 