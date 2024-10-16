#include "sbus.h"

/* SBUS object, writing SBUS */
bfs::SbusTx sbus_tx(&Serial0, D7, D6, true);

bfs::SbusData data;

// Variables to store received values
int32_t strafe_value = 992;
int32_t forward_value = 992;
int32_t turn_value = 992;

void setup() {
    Serial.begin(115200);
    /* Begin the SBUS communication */
    sbus_tx.Begin();
}

void parseSerialData() {
    static String buffer = "";
    while (Serial.available()) {
        char c = Serial.read();
        if (c == '<') {
            buffer = "";  // Start of new data
        } else if (c == '>') {
            // End of data, parse it
            int firstComma = buffer.indexOf(',');
            int secondComma = buffer.indexOf(',', firstComma + 1);
            
            if (firstComma != -1 && secondComma != -1) {
                strafe_value = buffer.substring(0, firstComma).toInt();
                forward_value = buffer.substring(firstComma + 1, secondComma).toInt();
                turn_value = buffer.substring(secondComma + 1).toInt();
                
                // Constrain values
                strafe_value = constrain(strafe_value, 192, 1792);
                forward_value = constrain(forward_value, 192, 1792);
                turn_value = constrain(turn_value, 192, 1792);
            }
            buffer = "";  // Clear buffer after parsing
        } else {
            buffer += c;  // Add character to buffer
        }
    }
}

void loop() {
    static int state = 0;
    static unsigned long StartTime = 0;

    int32_t _LOW = 192;
    int32_t _MID = 992;
    int32_t _HIGH = 1792;

    // Parse incoming serial data
    parseSerialData();

    if (state == 0) {
        // Initialize data channels to default (neutral) positions
        data.ch[0] = 992; // Rx
        data.ch[1] = 992; // Ry
        data.ch[2] = 992; // Ly
        data.ch[3] = 992; // Lx
        data.ch[4] = _MID; // CH5_STATE
        data.ch[5] = _MID; // CH6_STATE
        data.ch[6] = _HIGH; // CH7_STATE (channel 7 high)
        data.ch[7] = _MID; // CH8_STATE
        data.ch[8] = 1690;
        data.ch[9] = 154;

        // Set channel 7 high
        data.ch[6] = _HIGH;

        sbus_tx.data(data);
        sbus_tx.Write();

        // Move to next state
        state = 1;

        // Record the time
        StartTime = millis();

    } else if (state == 1) {
        // Wait until 1 second has passed
        if (millis() - StartTime >= 1000) {
            // Set channel 7 low
            data.ch[6] = _LOW;

            // Set values received from serial
            data.ch[3] = strafe_value; // strafe 
            data.ch[2] = forward_value; // forward
            data.ch[0] = turn_value; // turn 

            sbus_tx.data(data);
            sbus_tx.Write();

            // Move to next state
            state = 2;
        } else {
            // Keep sending data to keep channel 7 high
            sbus_tx.data(data);
            sbus_tx.Write();
            delay(10);
        }
    } else if (state == 2) {
        // Update values with the latest received from serial
        data.ch[3] = strafe_value; // strafe 
        data.ch[2] = forward_value; // forward
        data.ch[0] = turn_value; // turn 

        // Keep sending updated data
        sbus_tx.data(data);
        sbus_tx.Write();
        delay(10);
    }
}