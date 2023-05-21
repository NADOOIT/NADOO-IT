const sectionId = element.dataset.sectionId;
const sessionId = element.dataset.sessionId;

element.addEventListener('click', function() {
    fetch(`/signal/${sessionId}/${sectionId}/click/`, {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json',
            'X-Requested-With': 'XMLHttpRequest'
        },
        body: JSON.stringify({})
    });
});
