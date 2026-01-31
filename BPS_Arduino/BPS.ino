/**
 * Author: Ryanne Wilson
 * BPS Arduino for Props.
 * 
 */

 // INCLUDE
 #include <Arduino_CAN.h>
 void setup(){
    Serial.begin(115200)
    while(!Serial);

    if(!CAN.begin(CanBitRate::BR_250k)){
      Serial.println("CAN.begin(...) failed.");
      for(;;) {}
   }
 }

 void loop(){
   if(CAN.available()){
      CanMsg const msg = CAN.read();
      Serial.println(msg);
   }
 }