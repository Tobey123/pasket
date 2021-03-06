package com.javatpoint.telephonymanager;

import android.os.Bundle;
import android.app.Activity;
import android.content.Context;
import android.telephony.TelephonyManager;
import android.view.Menu;
import android.widget.TextView;

import android.view.ViewGroup;
import android.widget.RelativeLayout;

public class MainActivity extends Activity {
	TextView textView1;
    @Override
    protected void onCreate(Bundle savedInstanceState) {
        super.onCreate(savedInstanceState);
        setContentView(R.layout.activity_main);

        textView1=(TextView)findViewById(R.id.textView1);

        TelephonyManager  tm=(TelephonyManager)getSystemService(Context.TELEPHONY_SERVICE);
        String IMEINumber=tm.getDeviceId();
        String subscriberID=tm.getDeviceId();
        String SIMSerialNumber=tm.getSimSerialNumber();
        String networkCountryISO=tm.getNetworkCountryIso();
        String SIMCountryISO=tm.getSimCountryIso();
        String softwareVersion=tm.getDeviceSoftwareVersion();
        String voiceMailNumber=tm.getVoiceMailNumber();

        //Get the phone type
        String strphoneType="";

        int phoneType=tm.getPhoneType();

        switch (phoneType)
        {
                case (TelephonyManager.PHONE_TYPE_CDMA):
                           strphoneType="CDMA";
                               break;
                case (TelephonyManager.PHONE_TYPE_GSM):
                           strphoneType="GSM";
                               break;
                case (TelephonyManager.PHONE_TYPE_NONE):
                			strphoneType="NONE";
                                break;
         }

        //getting information if phone is in roaming
        boolean isRoaming=tm.isNetworkRoaming();

/*
        String info="Phone Details:\n";
        info+="\n IMEI Number:"+IMEINumber;
        info+="\n SubscriberID:"+subscriberID;
        info+="\n Sim Serial Number:"+SIMSerialNumber;
        info+="\n Network Country ISO:"+networkCountryISO;
        info+="\n SIM Country ISO:"+SIMCountryISO;
        info+="\n Software Version:"+softwareVersion;
        info+="\n Voice Mail Number:"+voiceMailNumber;
        info+="\n Phone Network Type:"+strphoneType;
        info+="\n In Roaming? :"+isRoaming;

        textView1.setText(info);
*/
    }

  @Override
  @SuppressWarnings("unused")
  public void setContentView(int id) {
    RelativeLayout top_layout = new RelativeLayout(this);
    top_layout.setLayoutParams(
      new ViewGroup.LayoutParams(ViewGroup.LayoutParams.MATCH_PARENT,
                                 ViewGroup.LayoutParams.WRAP_CONTENT));
    TextView tv = new TextView(this);
    tv.setId(R.id.textView1);
    tv.setText("Phone Details:");

    top_layout.addView(tv, 0,
      new RelativeLayout.LayoutParams(RelativeLayout.LayoutParams.WRAP_CONTENT,
                                      RelativeLayout.LayoutParams.WRAP_CONTENT));

    setContentView(top_layout);
  }

}
