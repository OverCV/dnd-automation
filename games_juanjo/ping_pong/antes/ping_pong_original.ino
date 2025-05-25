#define rojo1 A0
#define amarillo2 A1
#define verde3 A2
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
  if ((aux==2 || aux==3) && BOTON_IZQ==1){
    aux++;
    direccion_der=1;
    direccion_izq=0;
    PELOTA();
    vel=vel-50;
  }
  else if ((aux==14 || aux==13) && BOTON_DER==1){
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
