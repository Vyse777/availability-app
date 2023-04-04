# Angular Availability Web App
This Angular application will show the status of both the Pippy Pie and Whippy Pie.
You can also set labels for each Pi to easily differentiate them. This value gets stored in browser Local Storage, so it can be preserved when reloading the page.

---
This project was generated with [Angular CLI](https://github.com/angular/angular-cli) version 15.2.4.

# Development:

---
## Development server
Run `ng serve` for a dev server. Navigate to `http://localhost:4200/`. The application will automatically reload if you change any of the source files.

## Code scaffolding
Run `ng generate component component-name` to generate a new component. You can also use `ng generate directive|pipe|service|class|guard|interface|enum|module`.

## Build
Run `ng build` to build the project. The build artifacts will be stored in the `dist/` directory.

## Running unit tests
Run `ng test` to execute the unit tests via [Karma](https://karma-runner.github.io).

## Running end-to-end tests
Run `ng e2e` to execute the end-to-end tests via a platform of your choice. To use this command, you need to first add a package that implements end-to-end testing capabilities.

## Further help
To get more help on the Angular CLI use `ng help` or go check out the [Angular CLI Overview and Command Reference](https://angular.io/cli) page.

# Deployment & Use:

---
## Building & Deploying The App
First go update the MQTT hostname/URL in `app.module.ts`

Then, build the app with the Angular command `ng build --prod`.
The output dist can be used to host/run the application in any way you see fit.

Some recommendations include:
1) Dockerize it and run it in a Docker container wherever you want
2) Serve it with Dotnet, Java, Nginx, NodeJS, or any other million options for web servers that exist today
3) Host it on a cloud service such as AWS or Azure (Note: This app might not be fit for such a task as it would be internet exposed. The app was only ever really meant to operate intra-net)

## Use
Upon page load you'll see the two indicators for each Pi.

A white background within the Pi's card indicates the status of that Pi is unknown. This can happen if the MQTT broker has not been setup yet, or a connection issue has occured.

Other backgrounds follow the same concept as the keypads - Green, Yellow, Red

If you are special and want to try to break things, you can press the `=` key and unlock the status keys. This will allow you to update the status of either of the Pi's explicitly.
It's important to mention that the keypads (today) do not listen for their own status updates. This means if you change the status in this web-app the particular Pi you updated will still show the old status as it's 'current' status.

A better way would be to have the keypads listen for their own status updates (like how this app operates) to 'confirm' the publishing of its new status - only then update the local status/key color - then this issue is negated since the keypad will essentially be listening for status updates for its own status.

Maybe I will get to that some day... (as of 2023-04-04 I have still not gotten to it)
