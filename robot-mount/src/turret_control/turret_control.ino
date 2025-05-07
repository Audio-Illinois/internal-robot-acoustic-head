// Pin Definitions
#define STEP_PIN            10
#define RX_PIN              2
#define TX_PIN              3
#define EN_PIN              12
#define SENSOR_PIN          A1 // Inductive sensor

// Motor Constants
#define CURRENT             750 // 726
#define USTEPS_PER_STEP     4
#define STEPS_PER_REV       200
#define USTEPS_PER_REV      STEPS_PER_REV * USTEPS_PER_STEP
#define HOMING_ADJUSTMENT   12 // usteps, extra movement to center on homing sensor
#define HOMING_PAUSE        1000 // milliseconds, small pause to help observe and adjust homing adjustment
#define HOMING_SPEED        0.01

// Communication Constants
#define PULSE_WIDTH         200 // microseconds
#define CMD_HOME            "home"
#define CMD_MOVE            "move"
#define RPS_QSCALE          1000

// Library Includes
#include <TMC2208Stepper.h>
#include <SoftwareSerial.h>

// Global Objects and Variables
SoftwareSerial motorSerial(RX_PIN, TX_PIN);
TMC2208Stepper driver = TMC2208Stepper(&motorSerial);

// Check if home sensor is detecting something
bool isHomed() {
  return digitalRead(SENSOR_PIN) == HIGH;
}

// Send one PWM pulse
void _step() {
  digitalWrite(STEP_PIN, HIGH);
  delayMicroseconds(PULSE_WIDTH);
  digitalWrite(STEP_PIN, LOW);
}

// Base Utility: Run motor for a certain extent at a speed (rev/s)
void _rotate(int usteps, float rps, bool (*stop_cond)()=[]() {return 0;} ) {
  float abs_usteps = usteps;
  float usecPerStep = 1000000.0 / (rps * USTEPS_PER_REV);

  if (usteps < 0) {
      abs_usteps = -abs_usteps; // if negative, make positive
      driver.shaft(1); // Reverse Direction 
  }

  // Do nothing if movement might be out of bounds
  if (usecPerStep < PULSE_WIDTH) { return; }

  for (unsigned long i = 0; i < abs_usteps; i++) {
    _step();
    delayMicroseconds(usecPerStep);
    if (stop_cond()) {
      break;
    }
  }

  if (usteps < 0) { driver.shaft(0); } // Un-Reverse
}


// Basically a wrapper of _rotate with an exit flag
void Move(int usteps, float rps, int delay_ms=0) {
  delay(delay_ms);
  _rotate(usteps, rps);
  Serial.println(CMD_MOVE);
}


// Run calibration sequence until sensor is triggered
void Home() {
  if (!isHomed()) { // Avoid unecesmove adjustment (will un-home payload) if already homed
    _rotate(USTEPS_PER_REV, HOMING_SPEED, isHomed);
    delay(HOMING_PAUSE);
    Move(HOMING_ADJUSTMENT, HOMING_SPEED); // Rotate for slightly longer to properly center
  }
  Serial.println(CMD_HOME);
}


// PC-Arduino Communication
String ReadCommand() {
  String cmd = Serial.readStringUntil('\n');
  cmd.trim();
  return cmd;
}


int ReadValue() { return ReadCommand().toInt(); }


// Arduino Main Functions
void setup() {
  Serial.begin(115200);
  motorSerial.begin(115200);

  pinMode(STEP_PIN, OUTPUT);
  pinMode(EN_PIN, OUTPUT);
  pinMode(SENSOR_PIN, INPUT);

  driver.pdn_disable(1);                // Use UART communication
  driver.I_scale_analog(0);             // Use digital current control
  driver.rms_current(CURRENT, 1.0);          // Set current
  driver.toff(5);                        // Enable driver (low time)
  driver.en_spreadCycle(0);             // Use stealthChop mode
  driver.pwm_autoscale(1);              // Enable voltage regulator
  driver.mstep_reg_select(1);
  driver.microsteps(USTEPS_PER_STEP);   // Set microstep resolution
  driver.TPWMTHRS((uint32_t)0);                   // Never automatically go from stealthChop to spreadCycle
  driver.TPOWERDOWN((uint32_t)2);

  driver.push(); // Apply settings
}

void loop() {
  if (Serial.available()) {
    String cmd = ReadCommand();

    if (cmd==CMD_HOME) {
      Home();
    } else if (cmd==CMD_MOVE) {
      float rps = ReadValue() / (float)RPS_QSCALE;
      int usteps = ReadValue();
      int delay_ms = ReadValue();
      Move(usteps, rps, delay_ms);
    } else {
      delay(200);
      Serial.println(cmd);
    }
  }
}
