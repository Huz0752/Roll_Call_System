<template>
    <div>
        <h2>老師模式</h2>

        <!-- 登入表單 -->
        <div v-if="!isLoggedIn">
            <input type="text" v-model="username" placeholder="帳號" />
            <input type="password" v-model="password" placeholder="密碼" />
            <button @click="login">登入</button>
            <p v-if="loginError" style="color: red;">{{ loginError }}</p>
        </div>

        <!-- 登入成功後顯示的功能 -->
        <div v-else>
            <!-- 顯示時間到提示 -->
            <p v-if="timeUp" class="time-up">時間到!!!</p>

            <div>
                <input type="text" v-model="courseName" placeholder="輸入課程名稱" />
                <button @click="confirmCourseName">確認課程名稱</button>
                <p v-if="courseNameConfirmed" style="color: green;">已確認課程名稱: {{ courseName }}</p>
            </div>

            <!-- 倒數計時設定 -->
            <div>
                <input type="number" v-model="countdownMinutes" placeholder="輸入倒數分鐘數" />
                <button @click="confirmCountdown">確認時間</button>
                <p v-if="countdownConfirmed" style="color: green;">倒數時間已設定為: {{ countdownMinutes }} 分鐘</p>
            </div>

            <button @click="generatePin">生成 PIN 碼並上傳資料</button>
            <p v-if="pinCode">PIN 碼: {{ pinCode }} （有效期：{{ countdown }} 秒）</p>

            <div v-if="pinCode">
                <p>QR Code:</p>
                <canvas id="qrcode"></canvas>
            </div>

            <label for="fileUpload">上傳學生名單（.csv或.txt）</label>
            <input type="file" id="fileUpload" @change="uploadFile" accept=".csv, .txt" />
            <button @click="compareAttendance">比對出席名單</button>
        </div>
    </div>
</template>

<script>
import { nextTick, onUnmounted } from 'vue';
import QRCode from 'qrcode';
import axios from 'axios';

export default {
    data() {
        return {
            // 登入相關
            username: '',
            password: '',
            isLoggedIn: false,
            loginError: '',

            // 老師功能相關
            courseName: '',
            courseNameConfirmed: false,
            countdownMinutes: 5, // 預設倒數時間為 5 分鐘
            countdownConfirmed: false,
            pinCode: '',
            fileContent: '',
            timeUp: false, // 用於控制「時間到」的顯示

            // 計時器相關
            countdown: 300, // 倒數時間（以秒為單位），預設為 5 分鐘
            countdownInterval: null
        };
    },
    methods: {
        // 登入方法
        login() {
            if (this.username === 't' && this.password === '000') {
                this.isLoggedIn = true;
                this.loginError = '';
            } else {
                this.loginError = '帳號或密碼錯誤';
            }
        },

        // 確認課程名稱
        confirmCourseName() {
            if (this.courseName) {
                this.courseNameConfirmed = true;
                alert(`課程名稱已確認: ${this.courseName}`);
            } else {
                alert('請輸入課程名稱');
            }
        },

        // 確認倒數計時時間
        confirmCountdown() {
            if (this.countdownMinutes > 0) {
                this.countdown = this.countdownMinutes * 60; // 轉換為秒數
                this.countdownConfirmed = true;
                alert(`倒數時間已設定為 ${this.countdownMinutes} 分鐘`);
            } else {
                alert('請輸入有效的倒數時間（分鐘數）');
            }
        },

        // 生成 PIN 碼並上傳資料到後端
        async generatePin() {
            if (!this.countdownConfirmed) {
                this.countdown = 300; // 如果未確認倒數時間，使用預設的 5 分鐘（300 秒）
            }
            this.pinCode = Math.floor(1000 + Math.random() * 9000).toString(); // 生成4位數PIN
            this.timeUp = false; // 重置「時間到」提示
            this.startCountdown(); // 啟動倒數計時

            // 生成 QR Code
            await nextTick();
            const attendanceUrl = `http://192.168.0.118:8080/qr-login?isScanned=true`;
            const canvas = document.getElementById('qrcode');
            if (canvas) {
                QRCode.toCanvas(canvas, attendanceUrl, function (error) {
                    if (error) console.error(error);
                });
            }

            // 獲取今天的日期
            const today = new Date().toISOString().split('T')[0]; // 格式為 YYYY-MM-DD

            // 上傳資料到後端
            try {
                const response = await axios.post('http://localhost:5000/api/upload', {
                    date: today,
                    courseName: this.courseName,
                    pinCode: this.pinCode,
                    countdown: this.countdown
                });
                console.log('上傳成功', response.data);
            } catch (error) {
                console.error('上傳失敗', error);
            }

        },

        // 倒數計時器
        startCountdown() {
            clearInterval(this.countdownInterval);

            this.countdownInterval = setInterval(() => {
                if (this.countdown > 0) {
                    this.countdown--;
                } else {
                    clearInterval(this.countdownInterval);
                    this.pinCode = ''; // 時間結束後清除 PIN 碼
                    this.timeUp = true; // 顯示「時間到」
                }
            }, 1000);
        },

        // 上傳文件
        uploadFile(event) {
            const file = event.target.files[0];
            if (file) {
                const reader = new FileReader();
                reader.onload = (e) => {
                    this.fileContent = e.target.result;
                    alert('檔案上傳成功');
                };
                reader.readAsText(file);
            }
        },

        // 比對出席名單
        compareAttendance() {
            if (this.fileContent) {
                alert('開始比對出席名單'); // 比對邏輯可在此實現
            } else {
                alert('請先上傳學生名單');
            }
        }
    },
    mounted() {
        onUnmounted(() => {
            clearInterval(this.countdownInterval); // 清除計時器以防止內存泄漏
        });
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

/* 時間到提示樣式 */
.time-up {
    color: red;
    font-size: 2em;
    font-weight: bold;
    text-align: center;
    margin-top: 20px;
}
</style>
