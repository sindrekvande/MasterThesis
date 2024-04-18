timeStamp   = "datetime"
irrValue    = "irrValue"
ledPercent  = "ledPercent"

btConnect       = "btConnectedFlag"
#btDisconnect    = "btDisconnectFlag"
btPackets       = "btPackets"

adc1ch0 = "EH_IN_+_BUF"
adc1ch1 = "CSA_STORAGE_IN_+"
adc1ch2 = "V_BANK1"
adc1ch3 = "V_BANK2"
adc1ch4 = "V_BANK3"
adc1ch5 = "V_BANK4"
adc1ch6 = "V_BANK5"
adc1ch7 = "STORAGE_OUT"

adc2ch0 = "DCDC_OUT_BUF"
adc2ch1 = "EXT_AN_IN_1"
adc2ch2 = "EXT_AN_IN_2"
adc2ch3 = "EXT_CSA"
adc2ch4 = "CSA_EH_IN"
adc2ch5 = "CSA_STORAGE_IN"
adc2ch6 = "CSA_STORAGE_OUT"
adc2ch7 = "CSA_DCDC_OUT"
MPPT_EN = "MPPT_EN"
DCDC_EN = "DCDC_EN"
BANK1_EN = "BANK1_EN"
BANK2_EN = "BANK2_EN"
BANK3_EN = "BANK3_EN"
BANK4_EN = "BANK4_EN"
BANK5_EN = "BANK5_EN"

adc_channels = [adc1ch0, adc1ch1, adc1ch2, adc1ch3, adc1ch4, adc1ch5, adc1ch6, adc1ch7, adc2ch0, adc2ch1, adc2ch2, adc2ch3, adc2ch4, adc2ch5, adc2ch6, adc2ch7]

messages = {timeStamp:      0,
            irrValue:       0,
            ledPercent:     0,
            btConnect:      0,
            #btDisconnect:   0,
            btPackets:      0,

            adc1ch0: 0,
            adc1ch1: 0,
            adc1ch2: 0,
            adc1ch3: 0,
            adc1ch4: 0,
            adc1ch5: 0,
            adc1ch6: 0,
            adc1ch7: 0,

            adc2ch0: 0,
            adc2ch1: 0,
            adc2ch2: 0,
            adc2ch3: 0,
            adc2ch4: 0,
            adc2ch5: 0,
            adc2ch6: 0,
            adc2ch7: 0,
            MPPT_EN: 0,
            DCDC_EN: 0,
            BANK1_EN: 1,
            BANK2_EN: 0,
            BANK3_EN: 0,
            BANK4_EN: 0,
            BANK5_EN: 0,
            }

testActive = True

def resetBTmessages():
    #messages[btConnect] = 0
    #messages[btDisconnect] = 0
    messages[btPackets] = 0