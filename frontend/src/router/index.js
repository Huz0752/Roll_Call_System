import { createRouter, createWebHistory } from 'vue-router';
import HomeView from '../views/HomeView.vue';
import StudentLogin from '../components/StudentLogin.vue';
import TeacherPanel from '../components/TeacherPanel.vue';
import StudentQRLogin from '../components/StudentQRLogin.vue'; // 導入 StudentQRLogin.vue

const routes = [
  {
    path: '/',
    name: 'home',
    component: HomeView
  },
  {
    path: '/student-login',
    name: 'StudentLogin',
    component: StudentLogin
  },
  {
    path: '/teacher-panel',
    name: 'TeacherPanel',
    component: TeacherPanel
  },
  {
    path: '/qr-login', // 新增 QR Code 掃描後的登入頁面路由
    name: 'StudentQRLogin',
    component: StudentQRLogin
  }
];

const router = createRouter({
  history: createWebHistory(process.env.BASE_URL),
  routes
});

export default router;
