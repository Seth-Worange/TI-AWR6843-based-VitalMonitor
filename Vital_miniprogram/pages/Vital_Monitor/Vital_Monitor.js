// pages/Vital_Monitor.js
var util = require('../../utils/util.js');
Page({
  /**
   * 页面的初始数据
   */
  data: {
    result:'等待获取token',
    theday:"",
    breath_rate:'0.0',
    heart_rate:'0.0',
    intervalId: null, // 定时器ID
    breathRates: [], // 存储呼吸频率的数组
    heartRates: [], // 存储心跳频率的数组
    sleepQualityScore: 0, // 睡眠质量得分
    osaCount: 0,
    sleepAnalysis: '😁欢迎使用睡眠监测小程序！！！' // 睡眠健康分析结果
  },
  /**
   * 获取token按钮按下：
   */
  touchBtn_gettoken:function()
  {
      console.log("获取token按钮按下");
      this.setData({result:'获取token按钮按下'});
      this.gettoken();
  },
  /**
    * 获取token
    */
  gettoken:function(){
      console.log("开始获取...");//打印完整消息
      var that=this;  //这个很重要，在下面的回调函数中由于异步问题不能有效修改变量，需要用that获取
      wx.request({
          url: 'https://iam.cn-north-4.myhuaweicloud.com/v3/auth/tokens',
          data:'{"auth": {"identity": {"methods": ["password"],"password": {"user": {"name": "awr6843","password": "Wsc061731415926","domain": {"name": "CSDN-weixin_61879608"}}}},"scope": {"project": {"name": "cn-north-4"}}}}',
          method: 'POST', // OPTIONS, GET, HEAD, POST, PUT, DELETE, TRACE, CONNECT
          header: {'content-type': 'application/json' }, // 请求的 header 
          success: function(res){
              // success
              console.log("获取token成功");//打印完整消息
              console.log(res);//打印完整消息
              var token='';
              token=JSON.stringify(res.header['X-Subject-Token']);//解析消息头token
              token=token.replaceAll("\"", "");
              console.log("获取token=\n"+token);//打印token
              wx.setStorageSync('token',token);//把token写到缓存中,以便可以随时随地调用
          },
          fail:function(){
              // fail
              console.log("获取token失败");//打印完整消息
          },
          complete: function() {
              // complete
              console.log("获取token完成");//打印完整消息
          } 
      });
  },

  /**
   * 获取设备影子（start）按钮按下：
   */
  touchBtn_getshadow:function()
  {
      this.touchBtn_gettoken();
      console.log("获取设备影子按钮按下");
      this.setData({result:'获取设备影子按钮按下'});
      let that = this;
      this.setData({ breath_rate: '0.0', heart_rate: '0.0' }); // 重置数据
      this.data.intervalId = setInterval(function() {
      that.getshadow();
      }, 1000); // 每1秒执行一次
  },
  /**
   * 暂停（stop）按钮按下：
   */
  touchBtn_stop:function()
  {
      if (this.data.intervalId)
      {
          clearInterval(this.data.intervalId);
          this.data.intervalId = null;
          // 计算睡眠质量得分
          this.onCalculateSleepQuality();
          // 打印breathRates数组的长度
          console.log("breathRates数组长度: " + this.data.breathRates.length); 
          // 打印heartRates数组的长度
          console.log("heartRates数组长度: " + this.data.heartRates.length); 
      }
      console.log("读取停止！");
  },
  /**
   * 获取设备影子：
   */
  getshadow:function(){
      console.log("开始获取影子");//打印完整消息
      var that=this;  //这个很重要，在下面的回调函数中由于异步问题不能有效修改变量，需要用that获取
      var token=wx.getStorageSync('token');//读缓存中保存的token
      console.log("我的toekn:"+token);//打印完整消息
      wx.request({
          url: 'https://2dbd455ad3.st1.iotda-app.cn-north-4.myhuaweicloud.com/v5/iot/5c9687867fdb4346b3e0edab679fade3/devices/669e794b5830dc113ecdd3ca_device1/shadow',
          data:'',
          method: 'GET', // OPTIONS, GET, HEAD, POST, PUT, DELETE, TRACE, CONNECT
          header: {'content-type': 'application/json','X-Auth-Token':token }, //请求的header 
          success: function(res){// success
              // success
              console.log(res);//打印完整消息
              var shadow=JSON.stringify(res.data.shadow[0].reported.properties);
              console.log('设备影子数据：'+shadow);
              //以下根据自己的设备属性进行解析
              var breathRate=JSON.stringify(res.data.shadow[0].reported.properties.BreathRate);
              var heartRate=JSON.stringify(res.data.shadow[0].reported.properties.HeartRate);
              var osa=JSON.stringify(res.data.shadow[0].reported.properties.OsaCount);
              console.log('呼吸频率 = '+breathRate+' 次/分钟');
              console.log('心跳频率 = '+heartRate+' 次/分钟');
              console.log('暂停次数 = '+osa+' 次');

              // 将数据添加到数组中
              that.data.breathRates.push(parseFloat(breathRate));
              that.data.heartRates.push(parseFloat(heartRate));

              // 限制数组最大长度为1000
              if (that.data.breathRates.length > 1000) {
                that.data.breathRates.shift(); // 删除数组的第一个元素
                that.data.heartRates.shift(); // 删除数组的第一个元素
              }

              that.setData({breath_rate:breathRate});
              that.setData({heart_rate:heartRate});
              that.setData({osaCount:osa});
          },
          fail:function(){
              // fail
              console.log("获取影子失败");//打印完整消息
          },
          complete: function() {
              // complete
              console.log("获取影子完成");//打印完整消息
          } 
      });
  },

  /**
   * 设备命令下发按钮按下：
   */
  touchBtn_setCommand:function()
  {
      console.log("设备命令下发按钮按下");
      this.setData({result:'设备命令下发按钮按下'});
  },  

  // 计算睡眠质量的函数
  calculateSleepQuality: function () {
    const breathRates = this.data.breathRates;
    const heartRates = this.data.heartRates;

    // 计算平均值
    const calculateMean = function (array) {
      const sum = array.reduce((a, b) => a + b, 0);
      return sum / array.length;
    }

    // 计算标准差
    const calculateStandardDeviation = function (array, mean) {
      const variance = array.reduce((sum, value) => sum + Math.pow(value - mean, 2), 0) / array.length;
      return Math.sqrt(variance);
    }

    // 计算呼吸频率和心跳频率的平均值和标准差
    const meanBreathRate = calculateMean(breathRates);
    const meanHeartRate = calculateMean(heartRates);
    const stdBreathRate = calculateStandardDeviation(breathRates, meanBreathRate);
    const stdHeartRate = calculateStandardDeviation(heartRates, meanHeartRate);

    // 平稳性得分（标准差越小得分越高）
    const stabilityScore = 50 - (stdBreathRate + stdHeartRate);

    // 呼吸与心跳频率整体高低得分
    const breathRateScore = Math.max(0, 25 - Math.abs(meanBreathRate - 16)); 
    const heartRateScore = Math.max(0, 25 - Math.abs(meanHeartRate - 80));

    // 综合得分
    const totalScore = stabilityScore + breathRateScore + heartRateScore;

    // 限制得分范围在0到100之间
    return Math.round(Math.min(Math.max(totalScore, 0), 100));
  },

  // 触发计算睡眠质量得分的事件处理函数
  onCalculateSleepQuality: function () {
    const score = this.calculateSleepQuality();
    const analysis = this.generateSleepAnalysis(score);
    this.setData({ 
      sleepQualityScore: score,
      sleepAnalysis: analysis 
    });
    console.log("睡眠质量得分:", score);
    console.log("睡眠健康分析:", analysis);
  },

  // 根据得分生成睡眠健康分析结果
  generateSleepAnalysis: function (score) {
    let analysis = '';
    if (score >= 85) {
      analysis = '🤩您的睡眠质量非常好，呼吸与心跳频率稳定，整体健康状况良好。';
    } 
    else if (score >= 70) {
      analysis = '😄您的睡眠质量较好，但可以进一步改善，保持良好的作息习惯。';
    } 
    else if (score >= 50) {
      analysis = '🙂您的睡眠质量一般，可能存在一定的压力或不良习惯，建议改善睡眠环境和生活习惯。';
    } 
    else {
      analysis = '😫您的睡眠质量较差，呼吸与心跳频率波动较大，建议关注睡眠健康，必要时咨询医生。';
    }

    if(this.data.osaCount <= 5){
      analysis = analysis + '此外，在监测中出现了' + String(this.data.osaCount) + '次呼吸暂停。';
    }
    else if(this.data.osaCount > 5 && this.data.osaCount <= 15){
      analysis = analysis + '此外，在监测中出现了' + String(this.data.osaCount) + '次呼吸暂停, 需要注意可能为轻度呼吸暂停问题。';
    }
    else if(this.data.osaCount > 15 && this.data.osaCount <= 30){
      analysis = analysis + '此外，在监测中出现了' + String(this.data.osaCount) + '次呼吸暂停, 需要注意可能为中度呼吸暂停问题。';
    }
    else{
      analysis = analysis + '此外，在监测中出现了' + String(this.data.osaCount) + '次呼吸暂停, 需要注意可能为重度呼吸暂停问题，需要及时就医。';
    }
    return analysis;
  },

  // 微信小程序睡眠X秒
  sleep(numberMillis) { 
      var now = new Date(); 
      var exitTime = now.getTime() + numberMillis; 
      while (true) { 
        now = new Date(); 
        if (now.getTime() > exitTime) {
          return;
        }
      } 
    },

  onUnload: function() {
    this.touchBtn_stop(); // 页面卸载时停止循环
  },

  /**
   * 生命周期函数--监听页面加载
   */
  getToday: function () {
    let day =  util.formatTime(new Date()) ;
    let theday = day;  
    console.log(theday);
    this.setData({
     theDay: theday
    })
  },

  /**
   * 生命周期函数--监听页面加载
   */
  onLoad(options) {
    this.getToday();
  },

  /**
   * 生命周期函数--监听页面初次渲染完成
   */
  onReady() {

  },

  /**
   * 生命周期函数--监听页面显示
   */
  onShow() {

  },

  /**
   * 生命周期函数--监听页面隐藏
   */
  onHide() {

  },

  /**
   * 生命周期函数--监听页面卸载
   */
  onUnload() {

  },

  /**
   * 页面相关事件处理函数--监听用户下拉动作
   */
  onPullDownRefresh() {

  },

  /**
   * 页面上拉触底事件的处理函数
   */
  onReachBottom() {

  },

  /**
   * 用户点击右上角分享
   */
  onShareAppMessage() {

  }
})