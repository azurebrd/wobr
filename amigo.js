
function toggleShowHide(element) {
    document.getElementById(element).style.display = (document.getElementById(element).style.display == "none") ? "" : "none";
    return false;
}

function expandTermId(termId) {		// get the values of the children of the termId and load them in the children_ element
  var notQueriedElement = 'notQueried_' + termId;
  if (document.getElementById('notQueried_' + termId)) {		// this go number has not been queried
    var url = 'http://mangolassi.caltech.edu/~azurebrd/cgi-bin/testing/amigo/wobr/amigo.cgi?action=queryChildren&termId=' + termId;
    $(document.getElementById('children_' + termId)).load(url);				// load the children_<termId> UL with the list from the url
//     $('#children_' + termId).load(url);			// with this syntax it couldn't handle a : in the element ID
  }
  toggleShowHide('children_' + termId);				// always toggle to show or hide the UL children_<termId>
}


// NOT USING THESE ANYMORE
//
// function expandGoid(goNumber) {		// using goNumber instead of full goid because I can't figure out the syntax to have : in the element ID
//   if (document.getElementById('notQueried_' + goNumber)) {		// this go number has not been queried
//     var url = 'http://mangolassi.caltech.edu/~azurebrd/cgi-bin/testing/amigo/wobr/amigo.cgi?action=queryChildren&goNumber=' + goNumber;
//     $('#children_' + goNumber).load(url);				// load the children_<goNumber> UL with the list from the url
//   }
//   toggleShowHide('children_' + goNumber);				// always toggle to show or hide the UL children_<goNumber>
// }
