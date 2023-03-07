// ==UserScript==
// @name         Indeed Open Candidate Profiles
// @namespace    http://tampermonkey.net/
// @version      0.1
// @description  try to take over the world!
// @author       You
// @match        https://employers.indeed.com/candidates?id=*
// @icon         data:image/gif;base64,R0lGODlhAQABAAAAACH5BAEKAAEALAAAAAABAAEAAAICTAEAOw==
// @grant        GM_openInTab
// ==/UserScript==

(function() {
    'use strict';
        setTimeout(function() {

            //Get the table with all of the candidates
            var table = document.querySelector('[role="table"]');

            //Identify the size
            var num_loops = table.children.length;

            //Loop through the candidates
            // there are 2 more rows than there are candidates in Indeed so we start at 2
            (function myLoop(i) {
                //Wait 40 seconds between opening each candidate link
                setTimeout(function() {

                    //Target href of enclosed link
                    var candidate_href = table.children[i].querySelector('[data-testid="candidate-name"]').getAttribute('href');

                    // Open href in a new tab
                    candidate_href = "https://employers.indeed.com" + candidate_href;
                    GM_openInTab (candidate_href);

                    //If we are on the last candidate, check if there is html for another page of candidates
                    if (i == num_loops-1) {
                        console.log("Last Candidate");
                        var pageUL = document.querySelector('[data-testid="candidate-list-pagination"]').children[0];
                        var pageULSize = pageUL.children.length;
                        var nextPageButton = pageUL.children[pageULSize-1].children[0];

                        //reload page if it is not disabled
                        if (!nextPageButton.disabled) {
                            //press Next Page Button
                            nextPageButton.click();
                            //Reload page
                            location.reload();
                        }
                    }

                    //Increase i and run it back
                    if (i < num_loops-1) {i++; myLoop(i);}//  decrement i and call myLoop again if i > 0
                }, 40000)
        })(2);
    }, 3000)

})();