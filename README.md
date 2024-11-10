# Purpose

- Crawling data from the futures exchange for backtesting early morning ticks of the Mini Taiwan Index Futures (MTX) from 2020 to 2022.
- Custom strategies are defined, and various strategy combinations are used to determine entry and exit signals.
- The backtesting results include:
    - costs: the cost in points
    - profits: net profit in points after deducting costs
    - profit(%): some strategy combinations achieve up to 200% profit
    - days: the number of test days
    - days+: the number of profitable days
    - days-: the number of loss-making days
    - period: morning, focusing on early sessions
    - stock: MTX00, specifically for the Mini Taiwan Index Futures
  
![image](https://github.com/ChocolateBoy168/pyStock/blob/main/img/400%E5%A4%A9%E7%9A%84%E7%AD%96%E7%95%A5%E5%9B%9E%E6%B8%AC.png)

# Potential Risks

- The backtesting profits mentioned above do not take slippage into account.

# Strategy Combination Introduction and Examples

- Combination strategy = (use of volume from major players and retail investors) + (moving average application) + (take profit or stop loss)
- The combination strategy is formed by assembling various strategy seeds from JSON configuration files, allowing for flexible combinations. Example:

```text
  StraBvm[root(multi_b6)][bvm(aa_noBlock_1)][fomSumV(aa_3)][fomKma(aa_slope_in_60_20_10_5_out_60)][containNight(true)]
```

- The strategy seed [root(multi_b6)] is represented as follows:

```json 
{
  "version": "0.0.0",
  // Stop loss
  "stop_loss": 99,
  // Take profit
  "stop_profit": 199,
  // Morning session start entry time
  "morning_start_enter_time": 84500,
  // Morning session last entry time
  "morning_last_enter_time": 133000,
  // Morning session stop expired time
  "morning_stop_expired_time": 134430,
  // Night session start entry time
  "night_start_enter_time": 150000,
  // Night session last entry time
  "night_last_enter_time": 44500,
  // Night session stop expired time
  "night_stop_expired_time": 45939,
  // Whether to check both large and mini contracts together
  "request_multi_stockNo_ticks": true,
  "request_signal": {
    "stockNo": {
      "MTX00": {
        // Mini contract order volume greater than 20, indicating major player volume
        "master_unit": 20,
        // Mini contract order volume less than 3, indicating retail investor volume
        "slave_unit": 3
      },
      "TX00": {
        // Large contract order volume greater than 20, indicating major player volume
        "master_unit": 20,
        // Large contract order volume less than 3, indicating retail investor volume
        "slave_unit": 3
      }
    }
  }
}

```

- The strategy seed [bvm(aa_noBlock_1)] is represented as follows:

```json 
{
  "version": "0.0.0",
  "stockNos_achieve_of": {
    // Entry requires consideration of both MTX00 and TX00 together
    "in": "allOf",
    // Exit requires consideration of both MTX00 and TX00 together
    "out": "allOf"
  },
  "stockNo": {
    "MTX00": {
      "dams": [
        {
          // Enter position if in the mini contract there are more than 25 buy volumes within every 20 ticks
          "trigger": true,
          "name": "call1",
          "matches": [
            25
          ],
          "max_frame_size": 20,
          "blocks": []
        },
        {
          // Exit position if in the mini contract there are more than 25 sell volumes within every 20 ticks
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
        // Enter position if in the large contract there are more than 25 buy volumes within every 20 ticks
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
          // Exit position if in the large contract there are more than 25 sell volumes within every 20 ticks
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

- The strategy seed [fomSumV(aa_3)] is represented as follows:

```json 
{
  "version": "0.0.0",
  "stockNos_achieve_of": {
    // Entry conditions must be met for both the large and mini contracts
    "in": "allOf",
    // Exit conditions must be met for both the large and mini contracts
    "out": "allOf"
  },
  "info": "The 'in' and 'out' values are absolute. For example, if 250, it is 250 for 'call' and -250 for 'put'.",
  "stockNo": {
    "MTX00": {
      // Entry condition for the mini contract: cumulative volume must be greater than or equal to -500
      "in": -500,
      // Exit condition for the mini contract: cumulative volume must be less than or equal to -550
      "out": -550
    },
    "TX00": {
      // Entry condition for the large contract: cumulative volume must be greater than or equal to -500
      "in": -500,
      // Exit condition for the large contract: cumulative volume must be less than or equal to -550
      "out": -550
    }
  }
}

```

- The strategy seed [fomKma(aa_slope_in_60_20_10_5_out_60)] is represented as follows:

```json 
{
  "version": "0.0.0",
  "rate_of_second": 60,
  // Calculate the moving average of volume, with 60 seconds as the unit
  "rule": "slope",
  "stockNos_achieve_of": {
    "in": "allOf",
    "out": "allOf"
  },
  "stockNo": {
    "MTX00": {
      // For the mini contract, entry is allowed only when the slope of moving averages for 5 minutes, 10 minutes, 20 minutes, and 60 minutes are all upward. Exit occurs if the 60-minute volume slope turns downward.
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
      // For the large contract, entry is allowed only when the slope of moving averages for 5 minutes, 10 minutes, 20 minutes, and 60 minutes are all upward. Exit occurs if the 60-minute volume slope turns downward.
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

- The strategy seed [containNight(true)] means that the volume calculation starts from the night session
