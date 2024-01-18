<template>
  <div class="container">
    <div class="left-panel" :style="{ width: leftWidth + 'px' }">
      <!-- 左栏内容 -->
      <LeftContain />
    </div>
    <div class="divider" @mousedown="startResize"></div>
    <div class="right-panel" :style="{ width: rightWidth + 'px' }">
      <!-- 右栏内容 -->
      <RightContain />
    </div>
  </div>
</template>

<script setup>
import LeftContain from '../components/Left-Contain.vue'
import RightContain from '../components/Right-Contain.vue'
import { ref, computed } from 'vue';


const leftWidth = ref(260); // 初始左栏宽度
const rightWidth = computed(() => window.innerWidth - leftWidth.value);

const startResize = (event) => {
  const startX = event.clientX;
  const startWidth = leftWidth.value;
  const doResize = (e) => {
    const newWidth = startWidth + e.clientX - startX;
    if (newWidth > 0 && newWidth < window.innerWidth / 2) {
      leftWidth.value = newWidth;
    }
  };
  const stopResize = () => {
    window.removeEventListener('mousemove', doResize);
    window.removeEventListener('mouseup', stopResize);
  };
  window.addEventListener('mousemove', doResize);
  window.addEventListener('mouseup', stopResize);
};
</script>

<style>
.container {
  display: flex;
  height: 100vh;
}

.left-panel {
  background-color: #fff;
  overflow: auto;
}

.divider {
  background: linear-gradient(to right, rgba(175, 175, 175, 0.6), rgba(225, 225, 225, 0.6));
  width: 2px;
  cursor: col-resize;
  box-shadow: 0 0 4px rgba(0, 0, 0, 0.2);
  border-radius: 2px;
}


.right-panel {
  background-color: #fff;
  overflow: auto;
}
</style>