
// ==UserScript==
// @name         ZipRecruiter Open Candidate Profiles
// @namespace    http://tampermonkey.net/
// @version      0.1
// @description  Open Each candidate profile in a new tab
// @author       You
// @match        https://www.ziprecruiter.com/candidates?*
// @icon         data:image/gif;base64,R0lGODlhAQABAAAAACH5BAEKAAEALAAAAAABAAEAAAICTAEAOw==
// @grant        GM_xmlhttpRequest
// @grant        GM_openInTab
// @grant        GM_download
// @run-at document-body
// ==/UserScript==
/* globals jQuery, $ */

window.addEventListener('load', function() {
    'use strict';

    setTimeout(function() {
        var candidates_list = document.getElementsByClassName("candidates_list_items");
        console.log(candidates_list);
        var num_loops = candidates_list[0].childElementCount;

        (function myLoop(i) {
            setTimeout(function() {
                var candidate_href = candidates_list[0].childNodes[i].getElementsByClassName("candidate_photo")[0].href;
                console.log("opening candidate href: ", candidate_href);
                GM_openInTab (candidate_href); // open each one in a new window

                //TODO Close all the tabs once i == 0
                if (i < num_loops-1) {i++; myLoop(i);}//  decrement i and call myLoop again if i > 0
            }, 30000)
        })(0);
    }, 3000)
});




