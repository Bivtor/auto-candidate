
// ==UserScript==
// @name         Download HTML + Resume (ZipRecruiter)
// @namespace    http://tampermonkey.net/
// @version      0.1
// @description  Download html and resume from job page
// @author       You
// @match        https://www.ziprecruiter.com/contact/response/*
// @icon         data:image/gif;base64,R0lGODlhAQABAAAAACH5BAEKAAEALAAAAAABAAEAAAICTAEAOw==
// @grant        GM_download
// @grant        GM_xmlhttpRequest
// ==/UserScript==
/* globals jQuery, $ */


window.addEventListener('load', function() {
    'use strict';
      setTimeout(function() {
          var data = new Object();

          //Set source to ZipRecruiter
          data.source = "ZipRecruiter";

          //Download resume if there is one and set isResume to t/f
          try {
              document.getElementsByClassName('rlOriginalResumeLink common_action_button')[0].click(); //Click download resume button
              console.log("Downloaded Candidate resume");
              data.hasResume = true;
          }
          catch (exceptionVar) {
              data.hasResume = false;
              console.log("Candidate did not upload a resume");
                 }

          //Safely assign location variable, if none use default
          try {
              data.location = document.getElementsByClassName("location")[0].innerText;
            }
          catch (exceptionVar) {
                var location = document.getElementsByClassName("manage_job_link")[0].innerText;
                location = location.substr(location.search(" - ")+3, location.length);
                location = location.substr(0, location.search(",")+1);
                data.location = location;
                console.log("Candidate had no location, setting location to job post location");
            }

          //Get name, phone, email, ZR Link
          data.name = document.getElementsByClassName("name")[0].innerText;

          //Try to get phone number
          try {
              data.phone = document.getElementsByClassName("print_info email_phone")[0].getElementsByClassName("textPhone")[0].innerText;
            }
          catch (exceptionVar) {
                data.phone = "Not Listed";
                console.log("Candidate had no phone number");
            }

          //Try to get email
          try {
              data.email = document.getElementsByClassName("print_info email_phone")[0].getElementsByClassName("textEmail")[0].innerText;
            }
          catch (exceptionVar) {
                data.email = "Not Listed";
                console.log("Candidate had no Email listed");
            }

          //Get Date
          data.date = document.getElementsByClassName("text applied_date")[0].innerText;
          //Get PageLink
          data.pagelink = window.location.href;
          var formData=JSON.stringify(data);

          GM_xmlhttpRequest({
              method: "POST",
              url: "http://127.0.0.1:8000/runfunction",
              data: formData,
              headers: { 'accept': 'application/json', 'Content-Type':'application/json' },
              onload: function(response) {
                console.log(response);
              }
            });

          //close window after 40s
            setTimeout(function() {
                console.log("goodbye");
                window.close();
             }, 40000)
      }, 6000)

    //Download HTML and resume into correct location

});






