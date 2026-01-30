// change this if we wire it differently
#define RFM95_CS   8
#define RFM95_RST  4
#define RFM95_INT  2

#include "common.h"

void setup() {
    while (!Serial);
    Serial.begin(9600);
    Serial.println("Starting PONG board");
    pinMode(13, OUTPUT);
    initRadio();
}
void loop() {
    uint8_t len = RH_RF95_MAX_MESSAGE_LEN;
    if (rf.available()) {
        if (rf.recv((uint8_t*)buf, &len)) {
            if (len == MESSAGE_LEN && !memcmp(buf, BASE_PING, PREFIX_LEN)) {
                buf[4] = 'O'; // change the PING to PONG
    if (rf.available()) {
        if (rf.recv((uint8_t*)buf, &len)) {
            if (len == MESSAGE_LEN && !memcmp(buf, BASE_PING, PREFIX_LEN)) {
                buf[4] = 'O'; // change the PING to PONG

                long sendStart = micros();
                rf.send((uint8_t*)buf, MESSAGE_LEN);
                digitalWrite(13, HIGH);
                rf.waitPacketSent();
                digitalWrite(13, LOW);
                long sendEnd = micros();

                Serial.print("Sent in ");
                Serial.print(sendEnd - sendStart);
                Serial.println("us");
            } else {
                printUnexpected(len);
            }
        } else {
            Serial.println("Recv failed");
        }
    } else {
        // Serial.println("No available packet");
        //delay(10);
                Serial.print("Sent in ");
                Serial.print(sendEnd - sendStart);
                Serial.println("us");
            } else {
                printUnexpected(len);
            }
        } else {
            Serial.println("Recv failed");
        }
    } else {
        // Serial.println("No available packet");
        //delay(10);
    }
}