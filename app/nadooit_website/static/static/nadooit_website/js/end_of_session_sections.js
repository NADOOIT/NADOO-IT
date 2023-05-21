// Get the section and session id from the element's dataset
const sectionId = element.dataset.sectionId;
const sessionId = element.dataset.sessionId;

// Add an event listener for the 'revealed' event
element.addEventListener('revealed', function() {
    // Create a POST request to the 'end_of_session_sections' endpoint
    fetch(`/signal/${sessionId}/${sectionId}/end_of_session_sections/`, {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json',
            'X-Requested-With': 'XMLHttpRequest'
        }
    });
});
