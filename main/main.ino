#define rojo1 A2
#define amarillo2 A1
#define verde3 A0
#define verde4 2
#define verde5 3
#define verde6 4
#define verde7 5
#define verde8 6
#define verde9 7
#define verde10 8
#define verde11 9
#define verde12 10
#define verde13 11
#define amarillo14 12
#define rojo15 13
int BOTON_IZQ;
int BOTON_DER;
int aux=7, vel=200;
int direccion_der=1;
int direccion_izq=0;
void setup() {
  pinMode(rojo1,OUTPUT);
  pinMode(amarillo2,OUTPUT);
  pinMode(verde3,OUTPUT);
  pinMode(verde4,OUTPUT);
  pinMode(verde5,OUTPUT);
  pinMode(verde6,OUTPUT);
  pinMode(verde7,OUTPUT);
  pinMode(verde8,OUTPUT);
  pinMode(verde9,OUTPUT);
  pinMode(verde10,OUTPUT);
  pinMode(verde11,OUTPUT);
  pinMode(verde12,OUTPUT);
  pinMode(verde13,OUTPUT);
  pinMode(amarillo14,OUTPUT);
  pinMode(rojo15,OUTPUT);

  pinMode(A5,INPUT);
  pinMode(A4,INPUT);
}
void loop() {
  BOTON_IZQ=digitalRead(A5);
  BOTON_DER=digitalRead(A4);
  if (aux==2 && BOTON_IZQ==1){
    aux++;
    direccion_der=1;
    direccion_izq=0;
    PELOTA();
    vel=vel-50;
  }
  else if (aux==14 && BOTON_DER==1){
    aux--;
    direccion_der=0;
    direccion_izq=1;
    PELOTA();
  }
  else if (direccion_der==1){
    aux++;
    PELOTA();
  }
  else if (direccion_izq==1){
    aux--;
    PELOTA();
  }
  delay(vel);
}
void PELOTA(){
  switch (aux) {
  case 1: //pierdes el juego
    digitalWrite(rojo1,HIGH);
    digitalWrite(amarillo2,LOW);
  break;
  case 2: //amarillo izquierda
    digitalWrite(rojo1,LOW);
    digitalWrite(amarillo2,HIGH);
    digitalWrite(verde3,LOW);
  break;
  case 3:
    digitalWrite(amarillo2,LOW);
    digitalWrite(verde3,HIGH);
    digitalWrite(verde4,LOW);
  break;
  case 4:
    digitalWrite(verde3,LOW);
    digitalWrite(verde4,HIGH);
    digitalWrite(verde5,LOW);
  break;
  case 5:
    digitalWrite(verde4,LOW);
    digitalWrite(verde5,HIGH);
    digitalWrite(verde6,LOW);
  break;
  case 6:
    digitalWrite(verde5,LOW);
    digitalWrite(verde6,HIGH);
    digitalWrite(verde7,LOW);
  break;
  case 7:
    digitalWrite(verde6,LOW);
    digitalWrite(verde7,HIGH);
    digitalWrite(verde8,LOW);
  break;
  case 8:
    digitalWrite(verde7,LOW);
    digitalWrite(verde8,HIGH);
    digitalWrite(verde9,LOW);
  break;
  case 9:
    digitalWrite(verde8,LOW);
    digitalWrite(verde9,HIGH);
    digitalWrite(verde10,LOW);
  break;
  case 10:
    digitalWrite(verde9,LOW);
    digitalWrite(verde10,HIGH);
    digitalWrite(verde11,LOW);
  break;
  case 11:
    digitalWrite(verde10,LOW);
    digitalWrite(verde11,HIGH);
    digitalWrite(verde12,LOW);
  break;
  case 12:
    digitalWrite(verde11,LOW);
    digitalWrite(verde12,HIGH);
    digitalWrite(verde13,LOW);
  break;
  case 13:
    digitalWrite(verde12,LOW);
    digitalWrite(verde13,HIGH);
    digitalWrite(amarillo14,LOW);
  break;
  case 14: //amarillo derecha
    digitalWrite(verde13,LOW);
    digitalWrite(amarillo14,HIGH);
    digitalWrite(rojo15,LOW);
  break;
  case 15: //pierdes el juego
    digitalWrite(rojo15,HIGH);
    digitalWrite(amarillo14,LOW);
  break;

  default:
    digitalWrite(rojo15,HIGH);
    digitalWrite(rojo1,HIGH);
  break;
}
}

/*==============================================================================
 * SETUP()
 *============================================================================*/

void systemResetCallback()
{
  isResetting = true;

  // initialize a defalt state
  // TODO: option to load config from EEPROM instead of default

#ifdef FIRMATA_SERIAL_FEATURE
  serialFeature.reset();
#endif

  if (isI2CEnabled) {
    disableI2CPins();
  }

  for (byte i = 0; i < TOTAL_PORTS; i++) {
    reportPINs[i] = false;    // by default, reporting off
    portConfigInputs[i] = 0;  // until activated
    previousPINs[i] = 0;
  }

  for (byte i = 0; i < TOTAL_PINS; i++) {
    // pins with analog capability default to analog input
    // otherwise, pins default to digital output
    if (IS_PIN_ANALOG(i)) {
      // turns off pullup, configures everything
      setPinModeCallback(i, PIN_MODE_ANALOG);
    } else if (IS_PIN_DIGITAL(i)) {
      // sets the output to 0, configures portConfigInputs
      setPinModeCallback(i, OUTPUT);
    }

    servoPinMap[i] = 255;
  }
  // by default, do not report any analog inputs
  analogInputsToReport = 0;

  detachedServoCount = 0;
  servoCount = 0;

  /* send digital inputs to set the initial state on the host computer,
   * since once in the loop(), this firmware will only send on change */
  /*
  TODO: this can never execute, since no pins default to digital input
        but it will be needed when/if we support EEPROM stored config
  for (byte i=0; i < TOTAL_PORTS; i++) {
    outputPort(i, readPort(i, portConfigInputs[i]), true);
  }
  */
  isResetting = false;
}

void setup()
{
  Firmata.setFirmwareVersion(FIRMATA_FIRMWARE_MAJOR_VERSION, FIRMATA_FIRMWARE_MINOR_VERSION);

  Firmata.attach(ANALOG_MESSAGE, analogWriteCallback);
  Firmata.attach(DIGITAL_MESSAGE, digitalWriteCallback);
  Firmata.attach(REPORT_ANALOG, reportAnalogCallback);
  Firmata.attach(REPORT_DIGITAL, reportDigitalCallback);
  Firmata.attach(SET_PIN_MODE, setPinModeCallback);
  Firmata.attach(SET_DIGITAL_PIN_VALUE, setPinValueCallback);
  Firmata.attach(START_SYSEX, sysexCallback);
  Firmata.attach(SYSTEM_RESET, systemResetCallback);

  // to use a port other than Serial, such as Serial1 on an Arduino Leonardo or Mega,
  // Call begin(baud) on the alternate serial port and pass it to Firmata to begin like this:
  // Serial1.begin(57600);
  // Firmata.begin(Serial1);
  // However do not do this if you are using SERIAL_MESSAGE

  Firmata.begin(57600);
  while (!Serial) {
    ; // wait for serial port to connect. Needed for ATmega32u4-based boards and Arduino 101
  }

  systemResetCallback();  // reset to default config
}

/*==============================================================================
 * LOOP()
 *============================================================================*/
void loop()
{
  byte pin, analogPin;

  /* DIGITALREAD - as fast as possible, check for changes and output them to the
   * FTDI buffer using Serial.print()  */
  checkDigitalInputs();

  /* STREAMREAD - processing incoming messagse as soon as possible, while still
   * checking digital inputs.  */
  while (Firmata.available())
    Firmata.processInput();

  // TODO - ensure that Stream buffer doesn't go over 60 bytes

  currentMillis = millis();
  if (currentMillis - previousMillis > samplingInterval) {
    previousMillis += samplingInterval;
    /* ANALOGREAD - do all analogReads() at the configured sampling interval */
    for (pin = 0; pin < TOTAL_PINS; pin++) {
      if (IS_PIN_ANALOG(pin) && Firmata.getPinMode(pin) == PIN_MODE_ANALOG) {
        analogPin = PIN_TO_ANALOG(pin);
        if (analogInputsToReport & (1 << analogPin)) {
          Firmata.sendAnalog(analogPin, analogRead(analogPin));
        }
      }
    }
    // report i2c data for all device with read continuous mode enabled
    if (queryIndex > -1) {
      for (byte i = 0; i < queryIndex + 1; i++) {
        readAndReportData(query[i].addr, query[i].reg, query[i].bytes, query[i].stopTX);
      }
    }
  }

#ifdef FIRMATA_SERIAL_FEATURE
  serialFeature.update();
#endif
}
