import { IMqttServiceOptions, MqttModule } from 'ngx-mqtt';

import { NgModule } from '@angular/core';
import { FormsModule, ReactiveFormsModule } from '@angular/forms';
import { MatButtonModule } from '@angular/material/button';
import { MatCardModule } from '@angular/material/card';
import { MatInputModule } from '@angular/material/input';
import { MatProgressSpinnerModule } from '@angular/material/progress-spinner';
import { BrowserModule } from '@angular/platform-browser';
import { NoopAnimationsModule } from '@angular/platform-browser/animations';

import { AppRoutingModule } from './app-routing.module';
import { AppComponent } from './app.component';

export const connection: IMqttServiceOptions = {
  hostname: '', // Update with your MQTT server
  port: 9001,
  path: '/',
  clean: true, // Retain session
  connectTimeout: 4000,
  reconnectPeriod: 4000,
  clientId: 'availability-app-web-' + makeRandomString(),
}

function makeRandomString(ofLength: number = 13) {
  let possibleCharacters = "ABCDEFGHIJKLMNOPQRSTUVWXYZ1234567890-";
  let text = "";
  for (let i = 0; i < ofLength; i++) {
    text += possibleCharacters.charAt(Math.floor(Math.random() * possibleCharacters.length));
  }
  return text;
}

@NgModule({
  declarations: [
    AppComponent
  ],
  imports: [
    BrowserModule,
    AppRoutingModule,
    NoopAnimationsModule,
    MatCardModule,
    MatProgressSpinnerModule,
    MatButtonModule,
    MatInputModule,
    FormsModule,
    ReactiveFormsModule,
    MqttModule.forRoot(connection)
  ],
  providers: [],
  bootstrap: [AppComponent]
})
export class AppModule { }
