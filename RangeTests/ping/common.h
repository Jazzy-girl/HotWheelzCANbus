#include <SPI.h>
#include <RH_RF95.h>

#define RF95_FREQ 915.0

RH_RF95 rf(RFM95_CS, RFM95_INT);

const char* HEX_BYTES = "0123456789abcdef";
short COUNTER = 0;

const char* BASE_PING = "HW PING ";
const char* BASE_PONG = "HW PONG ";

#define PREFIX_LEN  8
#define MESSAGE_LEN  12
#define PAYLOAD_LEN 4

#define ERROR_PREFIX_LEN 27

#define BUFFER_LEN (RH_RF95_MAX_MESSAGE_LEN / 2)

char buf[BUFFER_LEN + 1];
char binaryBuf[BUFFER_LEN * 2 + ERROR_PREFIX_LEN + 1]; // two bytes per char + our message + null

bool isNonPrintable(char ch) {
    return ch < '\n' || ch > '~';
}

void initRadio() {
    pinMode(RFM95_RST, OUTPUT);
    digitalWrite(RFM95_RST, HIGH);
    delay(100);
    digitalWrite(RFM95_RST, LOW);
    delay(10);
    digitalWrite(RFM95_RST, HIGH);
    delay(10);

    while (!rf.init()) {
        Serial.println("Initialization failed!");
        // while (1);
    }

    while (!rf.setFrequency(RF95_FREQ)) {
        Serial.println("Frequency failed!");
        while (1);
    }

    rf.setTxPower(23, false); // set transmission power, 23 dBm (the highest strength)

    memcpy(binaryBuf, "Unexpected binary message: ", ERROR_PREFIX_LEN);
}

void printUnexpected(uint8_t len) {
    bool isBinary = false;
    char const* bPtr = buf; // pointer to the start of our buffer
    char const* const bEnd = bPtr + len; // pointer to the end of buffer
    while (bPtr < bEnd) if (isNonPrintable(*bPtr++)) { // iterate over the buffer, searching for a non-printable byte
        isBinary = true;
        break;
    }
    if (isBinary) {
        char* rPtr = buf;
        char* wPtr = binaryBuf + ERROR_PREFIX_LEN;
        while (rPtr < bEnd) {
            char b = *rPtr++;
            *wPtr++ = HEX_BYTES[b >> 4]; // get the hex character for the upper four bits
            *wPtr++ = HEX_BYTES[b & 15]; // get the hex character for the lower four bits
        }
        *wPtr = 0; // null-terminate the buffer
        Serial.println(binaryBuf);
    } else {
        buf[len] = 0; // null-terminate the buffer
        Serial.print("Unexpected printable message: ");
        Serial.println(buf);
    }
}