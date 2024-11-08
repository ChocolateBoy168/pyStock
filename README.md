# 目的

- 爬期貨交易所,從2020到2022年,爬兩年期間的小台指早盤ticks進行回測
- 自訂策略, 透過不同策略的組合, 判斷進出訊號
- 回測出的結果可以看到
    - costs: 是花費的成本點數
    - profits: 是扣掉成本後的獲利點數
    - 獲利(%): 有些組合策略獲利高達200%
    - days: 回測的天數
    - days+: 其中獲利的天數
    - days-: 其中損失的天數
    - period: morning 針對早盤
    - stock: MTX00 針對小台指數
  
![image](https://github.com/ChocolateBoy168/pyStock/blob/main/img/400%E5%A4%A9%E7%9A%84%E7%AD%96%E7%95%A5%E5%9B%9E%E6%B8%AC.png)

# 潛在風險

- 上面回測的獲利,是沒有考慮滑價.

# 策略組合介紹與範例

- 組合策略 = 主力與散戶的量運用 + 均線運用 + 停利或停損
- 組合策略是多個策略種子 strategy_seed 裡json配置檔 組合而成,可以任意搭配,範例:

```text
  StraBvm[root(multi_b6)][bvm(aa_noBlock_1)][fomSumV(aa_3)][fomKma(aa_slope_in_60_20_10_5_out_60)][containNight(true)]
```

- 策略種子 root(multi_b6).json 表示如下

```json 
{
  "version": "0.0.0",
  // 停損
  "stop_loss": 99,
  // 停利
  "stop_profit": 199,
  //早盤開始進場時間
  "morning_start_enter_time": 84500,
  //早盤最後進場時間
  "morning_last_enter_time": 133000,
  //早盤逾時出場時間
  "morning_stop_expired_time": 134430,
  //夜盤開始進場時間
  "night_start_enter_time": 150000,
  //夜盤最後進場時間
  "night_last_enter_time": 44500,
  //夜盤逾時出場時間
  "night_stop_expired_time": 45939,
  //是否大台小台一起判斷
  "request_multi_stockNo_ticks": true,
  "request_signal": {
    "stockNo": {
      "MTX00": {
        // 小台下單量大於20, 表示主力的量
        "master_unit": 20,
        // 小台下單小於3, 表示散戶的量
        "slave_unit": 3
      },
      "TX00": {
        // 大台下單量大於20, 表示主力的量
        "master_unit": 20,
        // 大台下單小於3, 表示散戶的量
        "slave_unit": 3
      }
    }
  }
}
```

- 策略種子 bvm(aa_noBlock_1).json 表示如下

```json 
{
  "version": "0.0.0",
  "stockNos_achieve_of": {
    //進場 MTX00 與 TX00 都要一起考量
    "in": "allOf",
    //出場 MTX00 與 TX00 都要一起考量
    "out": "allOf"
  },
  "stockNo": {
    "MTX00": {
      "dams": [
        {
          // 在小台中每20個tick中有量買進大於25就進場
          "trigger": true,
          "name": "call1",
          "matches": [
            25
          ],
          "max_frame_size": 20,
          "blocks": []
        },
        {
          // 在小台中每20個tick中有量賣出大於25就出場
          "trigger": true,
          "name": "put1",
          "matches": [
            -25
          ],
          "max_frame_size": 20,
          "blocks": []
        }
      ]
    },
    "TX00": {
      "dams": [
        // 在大台中每20個tick中有量買進大於25就進場
        {
          "trigger": true,
          "name": "call1",
          "matches": [
            25
          ],
          "max_frame_size": 20,
          "blocks": []
        },
        {
          // 在太台中,每20個tick中有量賣出大於25就出場
          "trigger": true,
          "name": "put1",
          "matches": [
            -25
          ],
          "max_frame_size": 20,
          "blocks": []
        }
      ]
    }
  }
}

```

- 策略種子 fomSumV(aa_3).json 表示如下

```json 
{
  "version": "0.0.0",
  "stockNos_achieve_of": {
    // 進場大台與小台條件都符合
    "in": "allOf",
    // 出場大台與小台條件都符合
    "out": "allOf"
  },
  "info": "in out 值是絕對值, ex: if 250 ,對call而言是250,對put而言是-250",
  "stockNo": {
    "MTX00": {
      // 小台只要量總和是-500以上就可進場
      "in": -500,
      // 小台只要量總和是-500以下就可出場
      "out": -550
    },
    "TX00": {
      // 大台只要量總和是-500以上就可進場
      "in": -500,
      // 大台只要量總和是-500以下就可出場
      "out": -550
    }
  }
}
```

- 策略種子 fomKma(aa_slope_in_60_20_10_5_out_60) 表示如下

```json 
{
  "version": "0.0.0",
  "rate_of_second": 60,
  ///計算量的均線, 以60秒為一個單位
  "rule": "slope",
  "stockNos_achieve_of": {
    "in": "allOf",
    "out": "allOf"
  },
  "stockNo": {
    "MTX00": {
      // 小台中, 5分/10分/20分/60分的均量 斜率都向上 才可進場, 遇到60分的量斜率若向下就出場 
      "in": [
        5,
        10,
        20,
        60
      ],
      "out": [
        60
      ]
    },
    "TX00": {
      // 大台中, 5分/10分/20分/60分的均量 斜率都向上 才可進場, 遇到60分的量斜率若向下就出場 
      "in": [
        5,
        10,
        20,
        60
      ],
      "out": [
        60
      ]
    }
  }
}

```

- 策略種子 containNight(true): 表示計算的量是從夜盤開始
