<template>
  <div>
    <!-- 登入表單 -->
    <div v-if="!isLoggedIn">
      <h2>學生登入</h2>
      <input type="text" v-model="username" placeholder="帳號" />
      <input type="password" v-model="password" placeholder="密碼" />
      <button @click="login">登入</button>
      <p v-if="loginError" style="color: red;">{{ loginError }}</p>
    </div>

    <!-- 登入成功後顯示 PIN 碼輸入 -->
    <div v-else>
      <h3>請輸入 PIN 碼進行點名</h3>
      <input type="text" v-model="pinCode" placeholder="輸入 PIN 碼" />
      <button @click="submitPin">點名</button>
      <p v-if="pinError" style="color: red;">{{ pinError }}</p>
    </div>
  </div>
</template>

<script>
import axios from 'axios';

export default {
  data() {
    return {
      // 登入相關
      username: '',
      password: '',
      isLoggedIn: false,
      loginError: '',

      // PIN 碼相關
      pinCode: '',
      pinError: '' // 錯誤提示
    };
  },
  methods: {
    // 登入方法
    login() {
      if (this.username === 's' && this.password === '000') {
        this.isLoggedIn = true;
        this.loginError = '';
      } else {
        this.loginError = '帳號或密碼錯誤';
      }
    },

    // 提交 PIN 碼並比較
    async submitPin() {
      if (this.pinCode) {
        try {
          // 從後端獲取當前老師設置的 PIN 碼
          const response = await axios.get('http://localhost:5000/api/get-pin');
          const serverPinCode = response.data.pinCode;

          // 比較 PIN 碼
          if (this.pinCode === serverPinCode) {
            this.pinError = '';
            alert('點名成功');

            // 獲取點名時間（按下「點名」按鈕的當下時間）
            const timestamp = new Date().toISOString();

            // 構建資料並上傳
            await axios.post('http://localhost:5000/api/attendance', {
              username: this.username,
              status: '成功',
              timestamp: timestamp
            });
            alert('點名資料已上傳');
          } else {
            this.pinError = 'PIN 碼不正確，請重試';
          }
        } catch (error) {
          console.error('錯誤:', error);
          this.pinError = '點名資料上傳失敗，請稍後再試';
        }
      } else {
        this.pinError = '請輸入 PIN 碼';
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

input {
  margin: 5px;
  padding: 5px;
}

p {
  margin: 5px;
  color: red;
}
</style>
