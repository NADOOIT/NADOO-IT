const sectionId = element.dataset.sectionId;
const sessionId = element.dataset.sessionId;

// Function to send vote signal
function sendVoteSignal(voteType, buttonElement) {
    // Clear previous highlight
    const upvoteButton = document.getElementById(`upvote-button-${sectionId}`);
    const downvoteButton = document.getElementById(`downvote-button-${sectionId}`);

    upvoteButton.classList.remove('highlighted-upvote');
    downvoteButton.classList.remove('highlighted-downvote');

    // Highlight the selected button
    if (voteType === 'upvote') {
        buttonElement.classList.add('highlighted-upvote');
    } else if (voteType === 'downvote') {
        buttonElement.classList.add('highlighted-downvote');
    }

    fetch(`/signal/${sessionId}/${sectionId}/${voteType}/`, {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json',
            'X-Requested-With': 'XMLHttpRequest'
        },
    });
}

// Add event listeners to the buttons
document.getElementById(`upvote-button-${sectionId}`).addEventListener('click', function() {
    sendVoteSignal('upvote', this);
});

document.getElementById(`downvote-button-${sectionId}`).addEventListener('click', function() {
    sendVoteSignal('downvote', this);
});
