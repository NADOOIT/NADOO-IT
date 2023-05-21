const sectionId = element.dataset.sectionId;
const sessionId = element.dataset.sessionId;
let enterTime = 0;

element.addEventListener('mouseenter', function() {
    enterTime = new Date().getTime();
});

element.addEventListener('mouseleave', function() {
    const leaveTime = new Date().getTime();
    const interactionTime = (leaveTime - enterTime) / 1000;

    fetch(`/signal/${sessionId}/${sectionId}/mouseleave/`, {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json',
            'X-Requested-With': 'XMLHttpRequest'
        },
        body: JSON.stringify({
            interaction_time: interactionTime
        })
    });
});
