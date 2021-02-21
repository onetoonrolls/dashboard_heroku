#include <WiFi.h>
#include <PubSubClient.h>

const char* ssid ="BoKKo"; ; //***change
const char* password ="imwin0849993286"; //***change
const char* mqtt_server = "test.mosquitto.org";
const int mqtt_port = 1883;
const char* mqtt_Client = "3e2529d4-40ed-4322-9833-8e6b0dccbb3d"; //***change
const char* mqtt_username = "pdNw9nVS2M12qmPm5K2xkoPLGvMAmWsH";  //***change
const char* mqtt_password = "tSO56gFCsHIrp1u5!lpzamnTTTGM!ZXG";  //***change

WiFiClient espClient;
PubSubClient client(espClient);

unsigned long last = 0;
const unsigned long tdelay = 1000;

char msg[100];

void reconnect();
void callback(char* ,byte* , unsigned int ); //get data from netpie

void setup()
{
  Serial.begin(115200);
  Serial.println("Connecting to ");
  Serial.println(ssid);
  WiFi.mode(WIFI_STA);
  WiFi.begin(ssid, password); // access wifi
  while(WiFi.status() !=WL_CONNECTED) //check disconnect
  {
    delay(500);
    Serial.print(".");  
  }
  Serial.println(" WiFi connected");
  Serial.println("IP address: ");
  Serial.println(WiFi.localIP());
  client.setServer(mqtt_server, mqtt_port);
  client.setCallback(callback);

  randomSeed(analogRead(0));
}

void loop()
{
  if(!client.connected())
      reconnect();
   client.loop();

   if(millis() - last  > tdelay )
   {
    int num = random(0, 100);

    //float humidityAir = dht.readHumidity(); //get air humidity
    //float temperature = dht.readTemperature(); // get air temp
    //int moisture = map(analogRead(MOISTURE), 0, 4095, 0, 100); //get soil humidity

    float humidityAir = random(0, 100);
    float temperature = random(0, 100);
    int moisture = random(0, 100);
    
    String info = "{\"topic\":\"Sensor\",\"data\": {\"humidityair\":" + String(7) + ",\"temperature\":" + String(8) +   ",\"moisture\":" + String(9) + "}}";
    
    info.toCharArray(msg, (info.length() + 1));
    client.publish("smartfarm-496", msg);
    Serial.println(info);
    last = millis();
   }
}

void reconnect()
{
  while (!client.connected()){
    Serial.print("Attempting MQTT connection...");
    if (client.connect(mqtt_Client, mqtt_username, mqtt_password))
      Serial.println("connected");
    else
      {
        Serial.print("failed, rc=");
        Serial.print(client.state());
        Serial.print("Try again in 5 sec");
        delay(5000);
      }
    }
}

void callback(char* topic,byte* payload, unsigned int length) //get data from netpie
{
  Serial.print("Message arrived [");
  Serial.print(topic);
  Serial.print("]: ");
  String msg;
  for (int i = 0; i < length; i++) {
    msg = msg + (char)payload[i];
  }
   Serial.println(msg);
}
