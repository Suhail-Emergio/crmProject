function resetTodaysLeadsInTwoMinutes() {
        const now = new Date();
        const midnight = new Date(now);
        midnight.setHours(24, 0, 0, 0);
        const millisecondsUntilMidnight = midnight - now;
        console.log('function loaded')
        setTimeout(function() {
            console.log("loaded at  midnight");
            fetch('/reset-todays-leads/')
                .then(response => {
                    if (!response.ok) {
                        throw new Error('Failed to reset todays_leads.');
                    }
                    console.log("success");
                })
                .catch(error => {
                    console.error('Error:', error);
                });
        }, millisecondsUntilMidnight);
}
resetTodaysLeadsInTwoMinutes();
