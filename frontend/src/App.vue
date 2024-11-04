<template>
  <div id="app">
    <!-- 顯示模式選擇組件 -->
    <RoleSelection @onSelectRole="navigateToRole" />
    <!-- 根據路由顯示對應組件 -->
    <router-view></router-view>
  </div>
</template>

<script>
import RoleSelection from './components/RoleSelection.vue';

export default {
  components: {
    RoleSelection
  },
  methods: {
    navigateToRole(selectedRole) {
      // 根據選擇的角色導航到不同路由
      if (selectedRole === 'student') {
        this.$router.push('/student-login');
      } else if (selectedRole === 'teacher') {
        this.$router.push('/teacher-panel');
      }
    }
  }
};
</script>

<style scoped>
button {
  margin: 5px;
  padding: 10px;
  font-size: 16px;
}
</style>
