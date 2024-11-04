<template>
  <div>
    <button @click="selectRole('student')">學生模式</button>
    <button @click="selectRole('teacher')">老師模式</button>
  </div>
</template>

<script>
export default {
  emits: ['onSelectRole'], // 定義 emit 事件
  methods: {
    selectRole(role) {
      this.$emit('onSelectRole', role); // 使用 $emit 傳遞選擇的模式給父組件
    }
  }
};
</script>
