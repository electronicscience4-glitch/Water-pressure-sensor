#include <Wire.h>
#include <Adafruit_GFX.h>
#include <Adafruit_SSD1306.h>

#define SCREEN_WIDTH 128
#define SCREEN_HEIGHT 64
#define OLED_RESET -1
Adafruit_SSD1306 display(SCREEN_WIDTH, SCREEN_HEIGHT, &Wire, OLED_RESET);

// پینەکان بۆ ١٠ LEDەکان
const int ledPins[] = {2, 3, 4, 5, 6, 7, 8, 9, 10, 11};
const int numLEDs = 10;

const float OffSet = 0.254;
float V = 0;
float P = 0;

// سنوورەکانی فشار بۆ LEDەکان
const float MAX_PRESSURE = 100.0;  // کیلۆپاسکاڵ
const float MIN_PRESSURE = 0.0;    // کیلۆپاسکاڵ

//*****************************************************************************
void setup() {
  Serial.begin(9600);
  Serial.println("/** Water pressure sensor ");
  
  // دامەزراندنی نمایشکەر
  display.begin(SSD1306_SWITCHCAPVCC, 0x3C);
  delay(2000);
  display.clearDisplay();
  display.setTextColor(WHITE);
  
  // ڕێکخستنی پینەکانی LED
  for (int i = 0; i < numLEDs; i++) {
    pinMode(ledPins[i], OUTPUT);
    digitalWrite(ledPins[i], LOW);  // خاموشکردنی هەموو LEDەکان لە سەرەتادا
  }
}

//*****************************************************************************
void updateLEDs(float pressure) {
  // چێکردنی فشار لە نێوان سنوورەکاندا
  if (pressure < MIN_PRESSURE) pressure = MIN_PRESSURE;
  if (pressure > MAX_PRESSURE) pressure = MAX_PRESSURE;
  
  // دۆزینەوەی ڕێژەی فشار (لە 0 بۆ 1)
  float ratio = (pressure - MIN_PRESSURE) / (MAX_PRESSURE - MIN_PRESSURE);
  
  // دۆزینەوەی ژمارەی LEDەکان کە دەبێت ڕووناکبن
  int ledsToLight = ratio * numLEDs;
  
  // ڕووناککردنی یان خاموشکردنی LEDەکان
  for (int i = 0; i < numLEDs; i++) {
    if (i < ledsToLight) {
      digitalWrite(ledPins[i], HIGH);  // ڕووناکی زیاد بکە
    } else {
      digitalWrite(ledPins[i], LOW);   // بیخەوێنە
    }
  }
}

//*****************************************************************************
void loop() {
  // خوێندنەوەی تێکڕای 10 خوێندنەوە بۆ کەمکردنەوەی ناڕێکی
  float sum = 0;
  for (int i = 0; i < 10; i++) {
    sum += analogRead(26);
    delay(10);
  }
  
  // هەژماری ڤۆڵت
  V = (sum / 10.0) * 5.00 / 1024.0;
  
  // هەژماری فشار
  P = (V - OffSet) * 250;
  
  // نوێکردنەوەی LEDەکان
  updateLEDs(P);
  
  // چاپکردن لەسەر Serial
  Serial.print("Voltage: ");
  Serial.print(V, 3);
  Serial.println("V");
  
  Serial.print("Pressure: ");
  Serial.print(P, 1);
  Serial.println(" KPa");
  
  Serial.print("LEDs lit: ");
  Serial.print((P / MAX_PRESSURE) * 10);
  Serial.println("/10");
  Serial.println();
  
  // نیشاندان لەسەر OLED
  display.clearDisplay();
  
  // ناونیشان
  display.setCursor(15, 0);
  display.setTextSize(1);
  display.println("Water Pressure");
  
  // نیشاندانی فشار
  display.setCursor(10, 20);
  display.setTextSize(2);
  display.print("P:");
  display.print(P, 1);
  display.println("KPa");
  
  // نیشاندانی ڤۆڵت
  display.setCursor(10, 40);
  display.setTextSize(1);
  display.print("V: ");
  display.print(V, 3);
  display.println("V");
  
  // نیشاندانی ڕێژەی LEDەکان
  display.setCursor(10, 55);
  float ledRatio = (P <= MAX_PRESSURE) ? (P / MAX_PRESSURE) : 1.0;
  display.print("LED: ");
  display.print((int)(ledRatio * 100));
  display.println("%");
  
  display.display();
  delay(500);  // پشوو بۆ نیشاندانی نەرم
}
