import { IMqttMessage, MqttService } from 'ngx-mqtt';
import { debounceTime, Subscription } from 'rxjs';

import { Component, HostListener } from '@angular/core';
import { FormControl } from '@angular/forms';

@Component({
  selector: 'app-root',
  templateUrl: './app.component.html',
  styleUrls: ['./app.component.scss']
})
export class AppComponent {
  masterMode = false; // Toggled if the user knows the special key to press!

  colorMap: any = { 'AVAILABLE': 'green', 'MODERATE': 'yellow', 'UNAVAILABLE': 'red', 'UNKNOWN': 'white' };

  pippyStatus = 'UNKNOWN';
  whippyStatus = 'UNKNOWN';

  // Form controls to allow the user to set a label on the particular Pi statuses (ex: 'User 1 Pie'). Defaults to the value stored in localStorage (null on first use)
  pippyFormControl = new FormControl(localStorage.getItem('pippyLabel'));
  whippyFormControl = new FormControl(localStorage.getItem('whippyLabel'));

  pippyPieStatusSubscription: Subscription | undefined;
  whippyPieStatusSubscription: Subscription | undefined;

  constructor(private mqttClient: MqttService) {
    // Subscribe to Pippy Pie status updates
    this.pippyPieStatusSubscription = this.mqttClient.observe('availability-app/pippy-pie/status').subscribe((message: IMqttMessage) => {
      console.log("Message for you sir! Message from Pippy Pie: " + message.payload.toString());
      this.pippyStatus = message.payload.toString();
    });

    // Subscribe to Whippy Pie status updates
    this.whippyPieStatusSubscription = this.mqttClient.observe('availability-app/whippy-pie/status').subscribe((message: IMqttMessage) => {
      console.log("Message for you sir! Message from Whippy Pie: " + message.payload.toString());
      this.whippyStatus = message.payload.toString();
    });

    // When the user updates the label we will save it to local storage so if the page is reloaded it will be remembered
    this.pippyFormControl.valueChanges.pipe(debounceTime(200)).subscribe(value => localStorage.setItem('pippyLabel', value as string))
    this.whippyFormControl.valueChanges.pipe(debounceTime(200)).subscribe(value => localStorage.setItem('whippyLabel', value as string))
  }

  updatePippyPie(status: string) {
    console.log('Sending Pippy Pie status update. Status: ' + status);
    // "Call back" will be the subscription we made in the constructor which will receive this message (if it goes through) and update the status accordingly
    this.mqttClient.unsafePublish('availability-app/pippy-pie/status', status, { qos: 0, retain: true });
  }

  updateWhippyPie(status: string) {
    console.log('Sending Whippy Pie status update. Status: ' + status);
    // "Call back" will be the subscription we made in the constructor which will receive this message (if it goes through) and update the status accordingly
    this.mqttClient.unsafePublish('availability-app/whippy-pie/status', status, { qos: 0, retain: true });
  }

  @HostListener('document:keyup.=', ['$event'])
  toggleMasterMode(event: KeyboardEvent) {
    this.masterMode = !this.masterMode;
  }
}
