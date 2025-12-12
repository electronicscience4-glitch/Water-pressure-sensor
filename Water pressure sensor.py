import machine
import time
import ssd1306
from machine import Pin, I2C, ADC

# ڕێکخستنی OLED
SCREEN_WIDTH = 128
SCREEN_HEIGHT = 64

# هەڵە: پینەکانی I2C چاک بکە
# بۆ پیکۆ، I2C0 زۆرجار لە پینەکانی 0 و 1 یان 4 و 5 یان 8 و 9 بەکاردەهێنرێت
try:
    i2c = I2C(0, scl=Pin(9), sda=Pin(8), freq=400000)
    display = ssd1306.SSD1306_I2C(SCREEN_WIDTH, SCREEN_HEIGHT, i2c)
    print("OLED initialized successfully")
except Exception as e:
    print(f"OLED initialization failed: {e}")
    # هەبوونی نمایشکەر تاقی بکەرەوە
    display = None

# ڕێکخستنی سێنسەری فشار (ADC)
sensor = ADC(Pin(26))  # بەکارهێنانی GP26 بۆ ADC

# ڕێکخستنی ١٠ LEDەکان
led_pins = [0, 1, 2, 3, 4, 5, 6, 7, 10, 11]  # پینەکان زیاد بکە
leds = []
for pin in led_pins[:10]:  # یەکەم ١٠ پین بەکاربهێنە
    try:
        leds.append(Pin(pin, Pin.OUT))
        print(f"LED on pin {pin} initialized")
    except Exception as e:
        print(f"Failed to initialize LED on pin {pin}: {e}")

# گۆڕینی Offset
OffSet = 0.254

# سنوورەکانی فشار بۆ LEDەکان (دەتوانێت بگۆڕدرێت)
MAX_PRESSURE = 100.0  # کیلۆپاسکاڵ
MIN_PRESSURE = 0.0    # کیلۆپاسکاڵ

def setup():
    print("/** Water pressure sensor demo **/")
    if display:
        display.fill(0)
        display.text("Starting...", 0, 0, 1)
        display.show()
    time.sleep(2)
    
    # خاموشکردنی هەموو LEDەکان لە سەرەتادا
    for led in leds:
        led.value(0)
    
    # تاقیکردنەوەی LEDەکان
    print("Testing LEDs...")
    for led in leds:
        led.value(1)
        time.sleep(0.1)
    time.sleep(0.5)
    for led in leds:
        led.value(0)

def update_leds(pressure):
    """
    نوێکردنەوەی ڕووناکی LEDەکان بەپێی ڕێژەی فشار
    """
    if not leds:
        return
    
    # دۆزینەوەی ڕێژەی فشار (لە 0 بۆ 1)
    if pressure < MIN_PRESSURE:
        pressure = MIN_PRESSURE
    if pressure > MAX_PRESSURE:
        pressure = MAX_PRESSURE
    
    ratio = (pressure - MIN_PRESSURE) / (MAX_PRESSURE - MIN_PRESSURE)
    
    # دۆزینەوەی ژمارەی LEDەکان کە دەبێت ڕووناکبن
    leds_to_light = int(ratio * len(leds))
    
    # ڕووناککردنی LEDەکان
    for i in range(len(leds)):
        if i < leds_to_light:
            leds[i].value(1)  # ڕووناکی زیاد بکە
        else:
            leds[i].value(0)  # بیخەوێنە

def read_sensor():
    """خوێندنەوەی نرخی سێنسەر بە شێوەیەکی نەرم"""
    # خوێندنەوەی تێکڕای 10 خوێندنەوە بۆ کەمکردنەوەی ناڕێکی
    total = 0
    samples = 10
    
    for i in range(samples):
        try:
            # خواندن لە ADC
            value = sensor.read_u16()
            total += value
        except Exception as e:
            print(f"Error reading ADC: {e}")
            total += 32767  # نرخی ناوەڕاست
        
        time.sleep(0.01)
    
    avg_value = total / samples
    
    # گۆڕینی بۆ ڤۆڵت
    # پیکۆ ADC: 16-bit (0-65535) و 3.3V
    V = (avg_value / 65535) * 3.3
    
    # هەژماری فشار
    P = (V - OffSet) * 250
    
    return V, P

def display_info(V, P):
    """نیشاندانی زانیاری لەسەر نمایشکەر"""
    if not display:
        return
    
    display.fill(0)
    
    # ناونیشان
    display.text("Water Pressure", 15, 0, 1)
    
    # نیشاندانی فشار
    display.text(f"P: {P:.1f} KPa", 10, 20, 1)
    
    # نیشاندانی ڤۆڵت
    display.text(f"V: {V:.3f} V", 10, 35, 1)
    
    # نیشاندانی ڕێژەی LEDەکان
    if P <= MAX_PRESSURE:
        led_ratio = P / MAX_PRESSURE
    else:
        led_ratio = 1.0
    
    display.text(f"LED: {int(led_ratio * 100)}%", 10, 50, 1)
    
    display.show()

def loop():
    # خوێندنەوەی سێنسەر
    V, P = read_sensor()
    
    # نوێکردنەوەی LEDەکان
    update_leds(P)
    
    # چاپکردن لەسەر Serial
    print("=" * 40)
    print(f"Voltage: {V:.3f} V")
    print(f"Pressure: {P:.1f} KPa")
    
    # ژمارەی LEDەکانی ڕووناک
    if P <= MAX_PRESSURE:
        leds_lit = int((P / MAX_PRESSURE) * len(leds))
    else:
        leds_lit = len(leds)
    
    print(f"LEDs lit: {leds_lit}/{len(leds)}")
    print(f"Raw ADC: {sensor.read_u16()}")
    
    # نیشاندان لەسەر OLED
    display_info(V, P)
    
    # کەمکردنەوەی پشوو بۆ نیشاندانی نەرم
    time.sleep(0.5)

# دانانی بەرنامەکە
if __name__ == "__main__":
    try:
        setup()
        print("System ready. Starting main loop...")
        while True:
            loop()
    except KeyboardInterrupt:
        print("\nProgram stopped by user")
        # خاموشکردنی هەموو LEDەکان
        for led in leds:
            led.value(0)
        if display:
            display.fill(0)
            display.text("Stopped", 40, 30, 1)
            display.show()
    except Exception as e:
        print(f"Unexpected error: {e}")
        # خاموشکردنی هەموو LEDەکان لە دۆخی هەڵەدا
        for led in leds:

            led.value(0)
