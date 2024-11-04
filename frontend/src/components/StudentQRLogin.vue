<template>
  <div>
    <h2>學生模式 - QR Code 登入</h2>

    <!-- 登入表單 -->
    <div v-if="!isLoggedIn">
      <input type="text" v-model="username" placeholder="帳號" />
      <input type="password" v-model="password" placeholder="密碼" />
      <button @click="login">登入</button>
      <p v-if="loginError" style="color: red;">{{ loginError }}</p>
    </div>

    <!-- 登入成功後的提示 -->
    <div v-else>
      <p>登入成功，點名已自動提交！</p>
      <p v-if="attendanceError" style="color: red;">{{ attendanceError }}</p>
      <p v-if="attendanceSuccess" style="color: green;">點名成功！</p>
    </div>
  </div>
</template>

<script>
import axios from 'axios';

export default {
  data() {
    return {
      username: '',
      password: '',
      isLoggedIn: false,
      loginError: '',
      isScanned: false, // 用來標記是否從 QR Code 進入
      attendanceError: '',
      attendanceSuccess: false
    };
  },
  methods: {
    // 登入方法
    async login() {
      if (this.username === 's' && this.password === '000') {
        this.isLoggedIn = true;
        this.loginError = '';

        // 檢查是否從 QR Code 掃描進入
        if (this.isScanned) {
          await this.submitAttendance(); // 自動提交點名紀錄
        }
      } else {
        this.loginError = '帳號或密碼錯誤';
      }
    },

    // 自動提交點名紀錄
    async submitAttendance() {
      try {
        // 獲取當前時間
        const timestamp = new Date().toISOString();

        // 上傳點名數據到後端
        const attendanceData = {
          username: this.username,
          status: '成功',
          timestamp: timestamp
        };
        await axios.post('http://localhost:5000/api/submitAttendance', attendanceData);

        // 顯示成功訊息
        this.attendanceSuccess = true;
        this.attendanceError = '';
      } catch (error) {
        console.error('點名過程中發生錯誤:', error);
        this.attendanceError = '無法成功提交點名紀錄，請稍後再試';
      }
    }
  },
  mounted() {
    // 檢查 URL 中是否包含 isScanned=true
    const urlParams = new URLSearchParams(window.location.search);
    this.isScanned = urlParams.get('isScanned') === 'true';
  }
};
</script>

<style scoped>
button {
  margin: 5px;
  padding: 10px;
  font-size: 16px;
}

input {
  margin: 5px;
  padding: 5px;
}
</style>
