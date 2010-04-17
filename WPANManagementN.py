import struct
import WPANNode
import WPAN

def get_voltage(addr_extended):
	out = {}
	sample = WPAN.ddo_get_param(addr_extended, '%V')              
	result = ord(sample[0]) * 256 + ord(sample[1])               
	voltage_level = adc_convert(result, "")
	out['U_mV'] = voltage_level
	return out	

def adc_convert(adc_data, sensor):  
    mVanalog = round((adc_data / 1023.) * 1200)
    temp_C_cal = 3.0
		  
    if sensor=='Temp':
        temp_C = (mVanalog - 500)/ 10. - temp_C_cal
	temp_F = temp_C * (9/5.) + 32		
	return temp_C, temp_F

    if sensor == 'Light':
	lux = mVanalog/3.		
	return lux
	
    if sensor == 'Humidity':
	hum = ((mVanalog * (108.2/33.2)) - 0.16)/(5*0.0062*1000)		
	return hum

    return mVanalog

def get_sensor_data(addr_extended):     
	out = {} 
	for pin in ['D1','D2','D3']:
		WPAN.ddo_set_param(addr_extended, pin, 2)

	buf = WPAN.ddo_get_param(addr_extended, 'is')

	buf1 = parse_is(buf)["AI1"]
	out['Light'] = round(adc_convert(buf1, "Light"))                                   
    
	buf2 = parse_is(buf)["AI2"]
	out['Temp_C'] = round(adc_convert(buf2, "Temp")[0])                                  
    
	buf3 = parse_is(buf)["AI3"]
   
	out['Humid'] = round(adc_convert(buf3, "Humidity"))  
	return out   

def parse_is(data):
	sets, digitalmask, analogmask = struct.unpack("!BHB", data[:4])
	data = data[4:]	
	retdir = {}			
	if digitalmask:
		datavals = struct.unpack("!H", data[:2])[0]
		data = data[2:]	
		currentDI = 0
		while digitalmask:
			if digitalmask & 1:
				retdir["DIO%d" % currentDI] = datavals & 1
			digitalmask >>= 1
			datavals >>= 1
			currentDI += 1	
	currentAI = 0
	while analogmask:
		if analogmask & 1:
			aval = struct.unpack("!H", data[:2])[0]
			data = data[2:]	
			retdir["AI%d" % currentAI] = aval
		analogmask >>= 1
		currentAI += 1 
			   
	return retdir		
