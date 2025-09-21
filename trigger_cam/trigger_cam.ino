const int buttonPin = 26;    // Pin donde está conectado el botón
int buttonState = 0;

void setup() {
  pinMode(buttonPin, INPUT); // Configura el pin con resistencia de pull-up interna
  Serial.begin(9600);
  delay(2000); // Espera a que se establezca la conexión serie
}

void loop() {
  buttonState = digitalRead(buttonPin);

  if (buttonState == HIGH) {
    // Si el botón está presionado
    Serial.println("capture");
    delay(500); // Pequeño retraso para evitar rebotes
    while (digitalRead(buttonPin) == HIGH); // Espera a que se suelte el botón
  }
}
