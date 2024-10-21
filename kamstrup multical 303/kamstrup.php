#!/usr/bin/php
<?php
// Reads data from a Kamstrup Multical 303, and publishes the values to MQTT (and domoticz)
$output = shell_exec("sudo /usr/local/bin/mbus-serial-request-data -d -b 2400 /dev/ttyUSB0 72"); 

$xmloutput=substr($output,strpos($output,'<MBusData>'));
$xmloutput = new SimpleXMLElement($xmloutput);

$counterID=$xmloutput->SlaveInformation->Id;

$energyValue_kWh=$xmloutput->DataRecord[0]->Value;
$volumeValue_m3=$xmloutput->DataRecord[1]->Value;
$supplyTempValue_cC=$xmloutput->DataRecord[6]->Value;
$returnTempValue_cC=$xmloutput->DataRecord[7]->Value;
$powerValue_hW=$xmloutput->DataRecord[9]->Value; //hectoWatt (watt * 100)
$flowValue_l_h=$xmloutput->DataRecord[11]->Value;

// device ids in domoticz
$IDXKamstrupSupplyTemp_C=60;
$IDXKamstrupReturnTemp_C=61;
$IDXKamstrupFlow_l_m=62; 
$IDXKamstrupEnergy_W_Wh=63;
$IDXKamstrupVolume_m3=64;


//Function to send to Domoticz, single value
function ud1($idx,$nvalue,$svalue1){
	file_get_contents('http://127.0.0.1:8080/json.htm?type=command&param=udevice&idx='.$idx.'&nvalue='.$nvalue.'&svalue='.$svalue1);
	usleep(250000);
}

// power meter value (current power W, and cumulative Wh)
function ud2($idx,$nvalue,$svalue1,$svalue2){
	file_get_contents('http://127.0.0.1:8080/json.htm?type=command&param=udevice&idx='.$idx.'&nvalue='.$nvalue.'&svalue='.$svalue1.';'.$svalue2);
	usleep(250000);
}


// C 
ud1($IDXKamstrupSupplyTemp_C,0,$supplyTempValue_cC/100);
ud1($IDXKamstrupReturnTemp_C,0,$returnTempValue_cC/100);

// l/min
ud1($IDXKamstrupFlow_l_m,0,$flowValue_l_h/60);

// W and Wh
ud2($IDXKamstrupEnergy_W_Wh,0,$powerValue_hW*100, $energyValue_kWh*1000);

// m3
ud1($IDXKamstrupVolume_m3,0,$volumeValue_m3);

shell_exec('mosquitto_pub -h MQTTBROKER -u USERNAME -P PASSWORD -t /kamstrup/water_aquarea -m \'{"supply_temp_C":' . $supplyTempValue_cC/100 . ',"return_temp_C":' . $returnTempValue_cC/100 . ',"flow_lpm":' . $flowValue_l_h/60 . ',"power_kW":' . $powerValue_hW/10 . ',"energy_kWh":' . $energyValue_kWh . ',"volume_m3":' . $volumeValue_m3 . ',"update_timestamp":' . time() . '}\'')
?>
