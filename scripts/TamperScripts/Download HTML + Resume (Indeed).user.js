// ==UserScript==
// @name         Download HTML + Resume (Indeed)
// @namespace    http://tampermonkey.net/
// @version      0.1
// @description  try to take over the world!
// @author       You
// @match        https://employers.indeed.com/candidates/*
// @icon         data:image/gif;base64,R0lGODlhAQABAAAAACH5BAEKAAEALAAAAAABAAEAAAICTAEAOw==
// @grant        GM_download
// @grant        GM_xmlhttpRequest
// ==/UserScript==
/* globals jQuery, $ */

(function() {
          setTimeout(function() {
                'use strict';
              var data = new Object();

              //Set Source as Indeed
              data.source = "Indeed";

              //Try to get Name, catch exception
              try{
                  const element = document.querySelector('[data-testid="namePlate-candidateName"]').innerText;
                  data.name = element;
                  console.log(element);
              } catch (e) {
                  data.name = "None";
                  console.log("Failed to get name");
                  console.log(e);
              }

              //Try to get location, catch exception
              try{
                  const element = document.querySelector('[data-testid="namePlate-leftPanel-location"]').innerText;
                  data.location = element;
                  console.log(element);
              } catch (e) {
                  data.location = "None";
                  console.log("Failed to get location");
                  console.log(e);
              }

              //Try to get email, catch exception
              try{
                  const element = document.querySelector('[id="namePlate-candidate-email"]').innerText;
                  data.email = element;
                  console.log(element);
              } catch (e) {
                  data.email = "None";
                  console.log("Failed to get email");
              }

              //Try to get date, catch exception
              try{
                  const element = document.querySelector('[data-storybook="AppliesNoteBlock"]').getElementsByTagName('div')[0].getElementsByTagName('strong')[0].innerText;
                  data.date = element;
                  console.log(element);
              } catch (e) {
                  data.date = "None";
                  console.log("Failed to get date");
              }

              //Download the Resume if it exists and set the resume attribute to true
               try {
                  const element = document.querySelector('[data-dd-action-name="download-resume-inline"]').click(); //Click download resume button
                  console.log("Downloaded Candidate resume");
                  data.hasResume = true;
               }
              catch (exceptionVar) {
                  data.hasResume = false;
                  console.log("Candidate did not upload a resume");
                 }

              //Get the link for this candidates page
              data.pagelink = window.location.href;


              //Try to get phone number, catch exception => This one is a little more complicated

              //IMPORTANT -- Try and Catch both contain the execute command contain to fix an error in which the phone number does not update for some reason
              try {
                  //Find the element and press the expand phone number button
                  const parentElement = document.querySelector('[data-shield-id="phone"]');
                  const buttonElement = parentElement.getElementsByTagName('button')[0];
                  buttonElement.click();
                  //Wait a second for this to be expanded (or half a second) and then target the inner text phone number
                  setTimeout(function() {
                    const number = document.querySelector('[class="css-14rdefe e1wnkr790"]').innerText;
                    console.log(number);
                    data.phone = number;

                  //Format formData
                  var formData=JSON.stringify(data);

                  //Print Data to console
                  console.log(formData);

                  //Send collected formdata to the server
                  GM_xmlhttpRequest({
                  method: "POST",
                  url: "http://127.0.0.1:8000/runfunction",
                  data: formData,
                  headers: { 'accept': 'application/json', 'Content-Type':'application/json' },
                  onload: function(response) {
                    console.log(response);
                  }
                });


                      },500);
              } catch (e) {
                  data.phone = "None";
                  console.log("Failed to get Phone Number");

                  //Format formData
                  var formData=JSON.stringify(data);

                  //Print Data to console
                  console.log(formData);

                  //Send collected formdata to the server
                  GM_xmlhttpRequest({
                  method: "POST",
                  url: "http://127.0.0.1:8000/runfunction",
                  data: formData,
                  headers: { 'accept': 'application/json', 'Content-Type':'application/json' },
                  onload: function(response) {
                    console.log(response);
                  }
                });
              }





              setTimeout(function() {
                window.close();
             }, 40000)

          },6000);
    // Your code here...
})();